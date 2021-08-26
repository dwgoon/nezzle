from qtpy import QtWidgets
from qtpy.QtWidgets import QGraphicsScene
from qtpy.QtWidgets import QGraphicsView
from qtpy.QtWidgets import QRubberBand
from qtpy.QtWidgets import QMenu



from qtpy.QtCore import Qt
from qtpy.QtGui import QKeyEvent
from qtpy.QtGui import QPixmapCache
from qtpy.QtGui import QPainter
from qtpy.QtGui import QTransform

from qtpy import QtCore
from qtpy.QtCore import Qt

import numpy as np


class GraphicsView(QGraphicsView):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)

        # The default of cache mode is no cache (0)
        self.setCacheMode(QGraphicsView.CacheBackground)

        QPixmapCache.setCacheLimit(102400)
        self.scale(1.0, 1.0)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)

        self.setAcceptDrops(True)


        # Create context menu
        if self.mw:
            self.pop_menu = QMenu(self)
            self.pop_menu.addMenu(self.mw.ui_menuAlign)  # Use the existing one.
            self.pop_menu.addMenu(self.mw.ui_menuGraphics)

    def on_context_menu(self, event):
        self.pop_menu.exec_(self.mapToGlobal(event.pos()))

    def enable_menu_align(self):
        """Turn on/off the alignment functionality.
        """
        items = self.scene().selected_movable_items()

        if self.mw and len(items) > 1:
            self.mw.ui_menuAlign.setEnabled(True)
        else:
            self.mw.ui_menuAlign.setEnabled(False)

    def mousePressEvent(self, event):
        if self.dragMode() == QGraphicsView.RubberBandDrag:

            item_clicked = self.scene().itemAt(self.mapToScene(event.pos()),
                                               QTransform())

            # Process the context menu actions such as alignment.
            if event.button() == Qt.RightButton:
                self.enable_menu_align()
                self.on_context_menu(event)
                # Should not return super().mousePressEvent(event) here.
                # Otherwise, the press event is processed under the drag mode.
                return

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragMode() == QGraphicsView.RubberBandDrag:
            item_under_mouse = self.scene().itemAt(
                self.mapToScene(event.pos()), QTransform())

        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        return super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        ad = -event.angleDelta().y()
        # factor = 1.41 ** (-ad / 240.0)
        if ad < 0:
            factor = 0.9
        else:
            factor = 1.1

        self.scale(factor, factor)

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == QtCore.Qt.Key_Space:
                self.setInteractive(False)  # Not to select any item
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                return

            items = self.scene().selected_movable_items()

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

    def keyReleaseEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == QtCore.Qt.Key_Space:
                self.setDragMode(QGraphicsView.RubberBandDrag)
                self.setInteractive(True)

    def _list_pos_x(self, items):
        return [item.x() for item in items]

    def _list_pos_y(self, items):
        return [item.y() for item in items]

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
            raise ValueError("Unknown direction for alignment: %s"
                             %(direction))

    def distribute_objects(self, direction):
        items_movable = self.scene().selected_movable_items()

        if direction == 'horizontal':  # x
            items_movable.sort(key=lambda obj: obj.x())
            x_max = max([item.x() for item in items_movable])
            x_min = min([item.x() for item in items_movable])
            gap_x = (x_max - x_min)/(len(items_movable)-1)
            for i, item in enumerate(items_movable):
                item.setX(x_min + i*gap_x)

        elif direction == 'vertical':  # y
            items_movable.sort(key=lambda obj: obj.y())
            y_max = max([item.y() for item in items_movable])
            y_min = min([item.y() for item in items_movable])
            gap_y = (y_max - y_min) / (len(items_movable) - 1)
            for i, item in enumerate(items_movable):
                item.setY(y_min + i*gap_y)
        else:
            raise ValueError("Unknown direction for distribution: %s"
                             %(direction))


class GraphicsScene(QGraphicsScene):
    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, parent, **kwargs)
        self.selectionChanged.connect(self.on_selection_changed)
        self.setBackgroundBrush(Qt.transparent)

        self.setItemIndexMethod(QGraphicsScene.NoIndex)

    def selected_movable_items(self):
        items_selected = self.selectedItems()
        return [item for item in items_selected if item.is_movable()]

    def on_selection_changed(self):
        view = self.views()[0]
        view.enable_menu_align()

# end of class
