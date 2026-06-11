import os
import sys
import time

import numpy as np

from qtpy.QtCore import Qt
from qtpy.QtCore import QRectF
from qtpy.QtCore import QTimer
from qtpy.QtCore import Slot, Signal
from qtpy import QtWidgets
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QGraphicsScene
from qtpy.QtWidgets import QGraphicsView
from qtpy.QtWidgets import QRubberBand
from qtpy.QtWidgets import QMenu
from qtpy.QtGui import QKeyEvent
from qtpy.QtGui import QPixmap
from qtpy.QtGui import QPixmapCache
from qtpy.QtGui import QPainter
from qtpy.QtGui import QTransform


from nezzle.history import History
from nezzle.graphics.nodes.basenode import BaseNode

# Diagnostics: NEZZLE_PERF_LOG=1 prints any interaction step slower than
# 20 ms to stderr; NEZZLE_NO_ZOOM_PREVIEW=1 disables the blit-zoom preview
# (live zooming) for A/B comparison.
_PERF_LOG = bool(os.environ.get("NEZZLE_PERF_LOG"))
_NO_ZOOM_PREVIEW = bool(os.environ.get("NEZZLE_NO_ZOOM_PREVIEW"))


def _perf(label, t_start):
    dt = (time.perf_counter() - t_start) * 1000.0
    if dt >= 20.0:
        print("[perf] %-28s %6.0f ms" % (label, dt), file=sys.stderr)


class GraphicsView(QGraphicsView):

    # Idle period after the last interactive step (wheel zoom, item drag,
    # pan) before full-quality rendering is restored.
    FAST_RENDER_RESTORE_DELAY_MS = 200

    # Item drags on scenes at least this large use the static-layer cache:
    # all non-moving items are rendered once into a viewport-sized pixmap
    # and hidden, so each drag frame repaints only the ~degree(node) moving
    # items over a blit instead of re-rasterizing every edge.
    STATIC_LAYER_MIN_ITEMS = 1000

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)

        # Interaction-aware render quality: antialiasing is the dominant
        # per-frame raster cost (measured 2.7-4x on drag/zoom for 600-1500
        # edge scenes), so it is suspended during continuous interaction and
        # restored by this timer once input pauses. Static image quality is
        # unaffected — the timeout repaints once at full quality.
        self._aa_restore_timer = QTimer(self)
        self._aa_restore_timer.setSingleShot(True)
        self._aa_restore_timer.setInterval(self.FAST_RENDER_RESTORE_DELAY_MS)
        self._aa_restore_timer.timeout.connect(self._restore_render_quality)

        # The default of cache mode is no cache (0)
        self.setCacheMode(QGraphicsView.CacheBackground)

        QPixmapCache.setCacheLimit(102400)
        self.scale(1.0, 1.0)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)

        # Wheel interaction must also hand keyboard focus to the view —
        # otherwise zooming over the view while e.g. the network tree was
        # last clicked leaves Space (pan mode) going to that other widget.
        self.setFocusPolicy(Qt.WheelFocus)

        self.setAcceptDrops(True)

        # Create context menu
        if self.mw:
            self.pop_menu = QMenu(self)
            self.pop_menu.addMenu(self.mw.ui_menuAlign)  # Use the existing one.
            self.pop_menu.addMenu(self.mw.ui_menuGraphics)

        self._pos_drag_start = None
        self._is_dragged = False
        self._item_clicked = None
        self._moved_by_key = False

        self._static_layer = None
        self._static_hidden = []
        # Once auto-scroll forces a drop mid-drag, stay dropped until
        # release: re-rendering the layer per scroll step would thrash.
        self._static_layer_blocked = False

        # Zoom preview: during a wheel burst on large scenes the viewport
        # is captured once and rescaled per notch instead of re-rasterizing
        # every item. When wheeling pauses, the layer is re-rendered sharp
        # (no AA, ~1 plain frame) at the settled transform and kept as a
        # STANDBY, so the next burst starts with zero capture cost; the
        # expensive antialiased repaint runs only after real idle.
        self._zoom_layer = None
        self._zoom_scene_rect = None
        self._zoom_connected_scene = None
        self._zoom_settle_timer = QTimer(self)
        self._zoom_settle_timer.setSingleShot(True)
        self._zoom_settle_timer.setInterval(500)
        self._zoom_settle_timer.timeout.connect(self._on_zoom_settled)

    def _enter_fast_render_mode(self):
        """Drop antialiasing for the duration of a continuous interaction.

        Cheap to call per input event: the hint is only toggled on the first
        call of a burst (setRenderHint schedules a full-viewport repaint, so
        repeated toggling must be avoided); subsequent calls just push the
        restore timer back.
        """
        if self.renderHints() & QPainter.Antialiasing:
            self.setRenderHint(QPainter.Antialiasing, False)
        self._aa_restore_timer.start()

    def _scene_too_large_for_aa(self):
        scene = self.scene()
        return (scene is not None
                and len(scene.items()) >= self.STATIC_LAYER_MIN_ITEMS)

    def _restore_render_quality(self):
        self._aa_restore_timer.stop()
        if self._scene_too_large_for_aa():
            # The antialiased quality pass blocks for seconds at this item
            # density while being nearly indistinguishable from plain
            # rendering — skip it entirely. (A standby zoom frame, if any,
            # stays up: it shows exactly what a live plain repaint would.)
            return
        if (self._zoom_layer is not None
                and not self._zoom_settle_timer.isActive()):
            # A standby zoom layer holds a non-antialiased frame; the
            # quality pass must paint the real scene.
            self._zoom_layer = None
            self._zoom_scene_rect = None
            self.viewport().update()
        if not (self.renderHints() & QPainter.Antialiasing):
            # Triggers one final full-quality repaint via updateAll().
            self.setRenderHint(QPainter.Antialiasing)

    def _install_static_layer(self):
        """Render every non-moving item once into a viewport-sized pixmap
        and hide them for the duration of the item drag.

        Kept visible (and live-painted) are: all selected items (hiding a
        selected item permanently destroys its selection), the movable
        selection, and for nodes their incident edges. Their children stay
        visible with them; everything else is blitted from the layer by
        drawBackground().
        """
        if self._static_layer is not None or self._static_layer_blocked:
            return

        scene = self.scene()
        if scene is None or len(scene.items()) < self.STATIC_LAYER_MIN_ITEMS:
            return

        movers = scene.selected_movable_items()
        if not movers:
            return

        keep = set(scene.selectedItems())
        for item in movers:
            keep.add(item)
            if isinstance(item, BaseNode):
                for edge in item.edges:
                    keep.add(edge)

        statics = [item for item in scene.items()
                   if item.parentItem() is None
                   and item.isVisible()
                   and item not in keep]
        if not statics:
            return

        # Opacity — not visibility — while building the layer: hiding the
        # grabbed item would break the active mouse grab, and hiding any
        # selected item destroys its selection.
        for item in keep:
            item.setOpacity(0.0)
        try:
            dpr = self.devicePixelRatioF()
            size = self.viewport().size()
            layer = QPixmap(int(size.width() * dpr),
                            int(size.height() * dpr))
            layer.setDevicePixelRatio(dpr)
            layer.fill(Qt.transparent)
            painter = QPainter(layer)
            painter.setRenderHints(self.renderHints())
            source = self.mapToScene(self.viewport().rect()).boundingRect()
            target = QRectF(0.0, 0.0, size.width(), size.height())
            scene.render(painter, target, source)
            painter.end()
        finally:
            for item in keep:
                item.setOpacity(1.0)

        for item in statics:
            item.setVisible(False)

        self._static_hidden = statics
        self._static_layer = layer
        # The view caches drawBackground output (CacheBackground), so the
        # cached content must be rebuilt with the layer blit.
        self.resetCachedContent()

    def _drop_static_layer(self):
        if self._static_layer is None:
            return
        for item in self._static_hidden:
            item.setVisible(True)
        self._static_hidden = []
        self._static_layer = None
        self.resetCachedContent()

    def _render_zoom_layer(self):
        """Render the scene at the current transform into a viewport-sized
        pixmap (no AA — one plain frame)."""
        if _PERF_LOG:
            t0 = time.perf_counter()
        result = self._render_zoom_layer_impl()
        if _PERF_LOG:
            _perf("zoom layer capture", t0)
        return result

    def _render_zoom_layer_impl(self):
        dpr = self.devicePixelRatioF()
        size = self.viewport().size()
        layer = QPixmap(int(size.width() * dpr), int(size.height() * dpr))
        layer.setDevicePixelRatio(dpr)
        layer.fill(Qt.transparent)
        painter = QPainter(layer)
        painter.setRenderHints(self.renderHints() & ~QPainter.Antialiasing)
        source = self.mapToScene(self.viewport().rect()).boundingRect()
        target = QRectF(0.0, 0.0, size.width(), size.height())
        self.scene().render(painter, target, source)
        painter.end()
        return layer, source

    def _begin_zoom_preview(self):
        """Activate blit-zooming; returns True when a layer is available.

        The standby layer from the previous burst is reused when it is
        still valid, so consecutive wheel bursts pay no capture cost.
        """
        scene = self.scene()
        if scene is None or len(scene.items()) < self.STATIC_LAYER_MIN_ITEMS:
            return False

        if self._zoom_connected_scene is not scene:
            if self._zoom_connected_scene is not None:
                try:
                    self._zoom_connected_scene.changed.disconnect(
                        self._on_zoom_scene_changed)
                except (TypeError, RuntimeError):
                    pass
            scene.changed.connect(self._on_zoom_scene_changed)
            self._zoom_connected_scene = scene

        if self._zoom_layer is None:
            self._zoom_layer, self._zoom_scene_rect = \
                self._render_zoom_layer()
        return True

    def _on_zoom_settled(self):
        """Wheel paused: refresh the layer sharp at the settled transform
        (one cheap no-AA frame, blitted 1:1) and keep it as a STANDBY so
        the next burst starts instantly. The expensive antialiased repaint
        is deferred to the AA-restore timer, i.e. until real idle."""
        if self._zoom_layer is None:
            return
        self._zoom_layer, self._zoom_scene_rect = self._render_zoom_layer()
        self.viewport().update()
        self._aa_restore_timer.start()

    def _drop_zoom_preview(self):
        """Discard the zoom layer (active or standby) and paint the live
        scene again."""
        if self._zoom_layer is None:
            return
        self._zoom_settle_timer.stop()
        self._zoom_layer = None
        self._zoom_scene_rect = None
        # The forced live repaint must not run antialiased: on dense scenes
        # an AA frame blocks for seconds right at the interaction (e.g. the
        # mouse press starting a drag). Fast mode paints it plain and the
        # quality pass returns after idle as usual.
        self._enter_fast_render_mode()
        self.viewport().update()

    def _on_zoom_scene_changed(self, *args):
        # Scene content changed while a standby frame is on screen: the
        # frame is stale. (During an active burst the preview may lag; it
        # is refreshed at settle time anyway.)
        if (self._zoom_layer is not None
                and not self._zoom_settle_timer.isActive()):
            self._drop_zoom_preview()

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if self._static_layer is not None:
            painter.save()
            painter.resetTransform()
            painter.drawPixmap(0, 0, self._static_layer)
            painter.restore()

    def paintEvent(self, event):
        if self._zoom_layer is None:
            if _PERF_LOG:
                t0 = time.perf_counter()
                ret = super().paintEvent(event)
                _perf("paint (live scene)", t0)
                return ret
            return super().paintEvent(event)

        if _PERF_LOG:
            t0 = time.perf_counter()
            self._paint_zoom_blit()
            _perf("paint (zoom blit)", t0)
            return
        self._paint_zoom_blit()

    def _paint_zoom_blit(self):

        # Zoom-preview frame: skip scene painting entirely and blit the
        # captured pixmap where its scene rect currently lands. Mapping
        # through viewportTransform() makes this exact under any
        # combination of scale steps and scrollbar adjustments.
        painter = QPainter(self.viewport())
        painter.fillRect(self.viewport().rect(), self.palette().base())
        vt = self.viewportTransform()
        tl = vt.map(self._zoom_scene_rect.topLeft())
        br = vt.map(self._zoom_scene_rect.bottomRight())
        # No SmoothPixmapTransform: bilinear filtering of a full-viewport
        # (DPR-scaled) pixmap is slow in the software raster engine, and
        # the preview is transient; standby frames blit 1:1 anyway.
        painter.drawPixmap(QRectF(tl, br), self._zoom_layer,
                           QRectF(self._zoom_layer.rect()))

    def scrollContentsBy(self, dx, dy):
        if self._static_layer is not None:
            # Auto-scroll during a drag moved the viewport: the cached layer
            # no longer matches. Drop it and stay dropped for this drag.
            self._drop_static_layer()
            self._static_layer_blocked = True
        if (self._zoom_layer is not None
                and not self._zoom_settle_timer.isActive()):
            # A standby frame does not cover regions exposed by scrolling.
            self._drop_zoom_preview()
        return super().scrollContentsBy(dx, dy)

    def resizeEvent(self, event):
        self._drop_static_layer()
        if (self._zoom_layer is not None
                and not self._zoom_settle_timer.isActive()):
            # Mid-burst resizes are usually just scrollbars appearing as
            # the zoom crosses the fit threshold; the blit mapping stays
            # exact and the settle frame re-covers the full new viewport,
            # so only a standby frame needs to be dropped here.
            self._drop_zoom_preview()
        return super().resizeEvent(event)

    def setScene(self, scene):
        super().setScene(scene)
        # Dense scenes never get the antialiased pass (see
        # _restore_render_quality) — also skip it for the very first
        # exposure, which otherwise blocks for seconds right after loading.
        self.setRenderHint(QPainter.Antialiasing,
                           not self._scene_too_large_for_aa())

    @Slot()
    def on_context_menu(self, event):
        self.pop_menu.exec_(self.mapToGlobal(event.pos()))

    def undo_current_scene(self):
        self.scene().history.undo()

    def redo_current_scene(self):
        self.scene().history.redo()

    def enable_menu_align(self):
        """Turn on/off the alignment functionality.
        """
        items = self.scene().selected_movable_items()

        if self.mw and len(items) > 1:
            self.mw.ui_menuAlign.setEnabled(True)
        else:
            self.mw.ui_menuAlign.setEnabled(False)

    def mousePressEvent(self, event):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            # Pan press: no selection happens (the view is non-interactive)
            # and no scene content changes, so the blit frame stays valid —
            # the pan preview can then start without a fresh capture. The
            # item hit-test below is also pointless here (and a linear scan
            # on unindexed dense scenes).
            self._item_clicked = None
            self._pos_drag_start = event.pos()
            return super().mousePressEvent(event)

        # A click must interact with the real scene, not a zoom preview.
        self._drop_zoom_preview()
        self._item_clicked = self.scene().itemAt(self.mapToScene(event.pos()), QTransform())
        if event.button() == Qt.LeftButton:
            self._pos_drag_start = event.pos()

            if self._item_clicked:
                super().mousePressEvent(event)
                self.scene().update_selected_items_old_positions()
                return

        if self.dragMode() == QGraphicsView.RubberBandDrag:
            # Process the context menu actions such as alignment.
            if event.button() == Qt.RightButton:
                self.enable_menu_align()
                self.on_context_menu(event)
                # Should not return super().mousePressEvent(event) here.
                # Otherwise, the press event is processed under the drag mode.
                return

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            return super().mouseMoveEvent(event)

        if event.buttons() != Qt.LeftButton:
            return super().mouseMoveEvent(event)

        if (event.pos() - self._pos_drag_start).manhattanLength() < 0.1: #QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        self._is_dragged = True
        self._enter_fast_render_mode()  # item drag or ScrollHandDrag pan

        if (self._item_clicked is not None
                and self.dragMode() == QGraphicsView.RubberBandDrag):
            # Item drag (not a rubber-band sweep, not a Space+drag pan).
            if _PERF_LOG:
                t0 = time.perf_counter()
                self._install_static_layer()
                _perf("static layer install", t0)
            else:
                self._install_static_layer()
        elif self.dragMode() == QGraphicsView.ScrollHandDrag:
            # Space+drag pan is a pure translation, so the blit preview
            # tracks it exactly: each pan step shifts the pixmap instead of
            # repainting the exposed strip through every item. Must run
            # BEFORE super() scrolls, so scrollContentsBy() sees an active
            # settle timer and keeps the layer.
            if self._begin_zoom_preview():
                self._zoom_settle_timer.start()

        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Restore the full live scene before any selection/history queries.
        self._drop_static_layer()
        self._static_layer_blocked = False

        if self._item_clicked and self._is_dragged:
            items = self.scene().selected_movable_items()
            num_items = len(items)
            if num_items > 0:
                self.scene().history.on_move_items_by_mouse(items)

        # Updating the old positions should be done after emitting the signal to History object.
        if self.dragMode() == QGraphicsView.RubberBandDrag:
            self.mw.ct_manager.update_console_vars()
            self.enable_menu_align()
            self.scene().update_selected_items_old_positions()

        self._is_dragged = False
        # No scene().update() here: item-level invalidation plus the
        # AA-restore repaint already cover every release scenario, and a
        # full-scene repaint per click is a whole frame on dense networks.
        self._restore_render_quality()
        return super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if not self.hasFocus():
            self.setFocus(Qt.MouseFocusReason)

        ad = event.angleDelta().y()
        if ad == 0:
            # Horizontal-only scroll: nothing to zoom.
            return super().wheelEvent(event)

        self._drop_static_layer()
        # Wheel up — including touchpad pinch-out, which the OS delivers as
        # a (Ctrl+)wheel-up — zooms in, matching platform convention.
        factor = 1.1 if ad > 0 else 0.9

        if _PERF_LOG:
            t0 = time.perf_counter()

        if not _NO_ZOOM_PREVIEW and self._begin_zoom_preview():
            # Large scene: the transform changes for real, but paintEvent
            # blits the captured pixmap instead of re-rasterizing every
            # item; a sharp frame is rendered when wheeling pauses and the
            # antialiased repaint waits for real idle.
            #
            # The settle timer must run BEFORE scale(): scale() adjusts the
            # scrollbars, and scrollContentsBy() treats a zoom layer with
            # no active settle timer as a stale standby and drops it.
            self._zoom_settle_timer.start()
            self.scale(factor, factor)
        else:
            self._enter_fast_render_mode()
            self.scale(factor, factor)

        if _PERF_LOG:
            _perf("wheelEvent", t0)
        return super().wheelEvent(event)

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Space:
                # Entering pan mode changes nothing in the scene, so any
                # standby blit frame stays valid — dropping it here forced
                # a full repaint before the hand cursor could even appear.
                self.setInteractive(False)  # Not to select any item
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                return

            # Move the selected items with arrow keys
            if event.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]:
                # Item moves must show live: discard the blit frame.
                self._drop_zoom_preview()

                if not event.isAutoRepeat():
                    self.scene().update_selected_items_old_positions()

                items = self.scene().selected_movable_items()
                if len(items) <= 0:
                    return
                self._enter_fast_render_mode()
                if event.key() == Qt.Key_Up:
                    for item in items:
                        item.setY(item.y() - 1)
                elif event.key() == Qt.Key_Down:
                    for item in items:
                        item.setY(item.y() + 1)
                elif event.key() == Qt.Key_Left:
                    for item in items:
                        item.setX(item.x() - 1)
                elif event.key() == Qt.Key_Right:
                    for item in items:
                        item.setX(item.x() + 1)

                self._moved_by_key = True
            # end of if

    def keyReleaseEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Space:
                self.setDragMode(QGraphicsView.RubberBandDrag)
                self.setInteractive(True)

            if not event.isAutoRepeat() and event.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]:
                items = self.scene().selected_movable_items()
                num_items = len(items)
                if self._moved_by_key and num_items > 0:
                    self.scene().history.on_move_items_by_key(items)
                    self._moved_by_key = False

    def _list_pos_x(self, items):
        return [item.x() for item in items]

    def _list_pos_y(self, items):
        return [item.y() for item in items]

    def _list_pos(self, items):
        return [item.pos() for item in items]

    def _set_items_pos_x(self, items, aggfunc):
        pos_x = aggfunc(self._list_pos_x(items))
        for item in items:
            item.setX(pos_x)

    def _set_items_pos_y(self, items, aggfunc):
        pos_y = aggfunc(self._list_pos_y(items))
        for item in items:
            item.setY(pos_y)

    def align_objects(self, direction):
        items = self.scene().selected_movable_items()

        if direction == 'left':
            self._set_items_pos_x(items, min)
        elif direction == 'right':
            self._set_items_pos_x(items, max)
        elif direction == 'center':
            self._set_items_pos_x(items, np.average)
        elif direction == 'top':
            self._set_items_pos_y(items, min)
        elif direction == 'bottom':
            self._set_items_pos_y(items, max)
        elif direction == 'middle':
            self._set_items_pos_y(items, np.average)
        else:
            raise ValueError("Unknown direction for alignment: %s"%(direction))

        self.scene().history.on_move_items_by_mouse(items)

    def distribute_objects(self, direction):
        items = self.scene().selected_movable_items()

        if direction == 'horizontal':  # x
            items.sort(key=lambda obj: obj.x())
            x_max = max([item.x() for item in items])
            x_min = min([item.x() for item in items])
            gap_x = (x_max - x_min) / (len(items) - 1)
            for i, item in enumerate(items):
                item.setX(x_min + i*gap_x)
                item.update()

        elif direction == 'vertical':  # y
            items.sort(key=lambda obj: obj.y())
            y_max = max([item.y() for item in items])
            y_min = min([item.y() for item in items])
            gap_y = (y_max - y_min) / (len(items) - 1)
            for i, item in enumerate(items):
                item.setY(y_min + i*gap_y)
                item.update()

        else:
            raise ValueError("Unknown direction for distribution: %s"%(direction))

        self.scene().history.on_move_items_by_mouse(items)


class GraphicsScene(QGraphicsScene):

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, parent, **kwargs)
        self.setBackgroundBrush(Qt.transparent)
        self.setItemIndexMethod(QGraphicsScene.NoIndex)

        self._history = History(self)

    @property
    def view(self):
        return self.views()[0]

    @property
    def history(self):
        return self._history

    def selected_movable_items(self):
        items_selected = self.selectedItems()
        return [item for item in items_selected if item.is_movable()]

    def update_selected_items_old_positions(self):
        items = self.selectedItems()  # Don't use selected_movable_items()
        if len(items) == 0:
            return

        for item in items:
            if item.is_movable():
                item["_OLD_POS"] = item.pos()

            item.update_children_old_positions()


# end of class
