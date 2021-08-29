import numpy as np

from qtpy.QtCore import Qt
from qtpy.QtCore import Slot, Signal
from qtpy import QtWidgets
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QGraphicsScene
from qtpy.QtWidgets import QGraphicsView
from qtpy.QtWidgets import QRubberBand
from qtpy.QtWidgets import QMenu
from qtpy.QtGui import QKeyEvent
from qtpy.QtGui import QPixmapCache
from qtpy.QtGui import QPainter
from qtpy.QtGui import QTransform

from nezzle.command.history import History


class GraphicsView(QGraphicsView):

    #items_moved = Signal(list, list)
    #items_moved_by_mouse = Signal(list)
    #items_moved_by_key = Signal(list)
    #items_removed = Signal(list)

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

        self._pos_drag_start = None
        self._is_dragged = False
        self._item_clicked = None
        self._moved_by_key = False

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
        self._item_clicked = self.scene().itemAt(self.mapToScene(event.pos()), QTransform())
        print("Item Clicked:", self._item_clicked)

        if event.button() == Qt.LeftButton:
            print("Mouse Pressed with Left Button!")
            self._pos_drag_start = event.pos()

            if self._item_clicked:
                self.scene().update_old_positions_selected_items()

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
        #modifiers = QApplication.keyboardModifiers()
        if event.modifiers() == Qt.ControlModifier:
            return

        if event.buttons() != Qt.LeftButton:
            return

        if (event.pos() - self._pos_drag_start).manhattanLength() >= QApplication.startDragDistance():
            self._is_dragged = True

        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._item_clicked and self._is_dragged:
            items = self.scene().selected_movable_items()
            if len(items) != 0:
                # self.items_moved_by_mouse.emit(items)
                self.scene().history.on_items_moved_by_mouse(items)
                print("Emit items moved signal")

        # Updating the old positions should be done after emitting the signal to History object.
        if self.dragMode() == QGraphicsView.RubberBandDrag:
            self.mw.ct_manager.update_console_vars()
            self.enable_menu_align()
            self.scene().update_old_positions_selected_items()

        self._is_dragged = False
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
            if event.key() == Qt.Key_Space:
                self.setInteractive(False)  # Not to select any item
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                return

            # Move the selected items with arrow keys
            if event.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]:

                if not event.isAutoRepeat():
                    self.scene().update_old_positions_selected_items()

                items = self.scene().selected_movable_items()
                if len(items) <= 0:
                    return
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
                if self._moved_by_key and len(items) > 0:
                    #self.items_moved_by_key.emit(items)
                    self.scene().items_moved_by_key(items)
                    print("Emit items moved signal")
                    self._moved_by_key = False
                    #self.scene().update_old_positions_selected_items()  # Record each step

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
            raise ValueError("Unknown direction for distribution: %s"%(direction))


class GraphicsScene(QGraphicsScene):

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, parent, **kwargs)
        #self.selectionChanged.connect(self.on_selection_changed)
        self.setBackgroundBrush(Qt.transparent)
        self.setItemIndexMethod(QGraphicsScene.NoIndex)

        self._history = History(self)

    @property
    def view(self):
        return self.views()[0]

    @property
    def history(self):
        return self._history

    def addItem(self, item):
        item["_OLD_POS"] = item.pos()
        return super().addItem(item)

    def selected_movable_items(self):
        items_selected = self.selectedItems()
        return [item for item in items_selected if item.is_movable()]

    # def on_selection_changed(self):
    #     pass
        # view = self.views()[0]
        # view.enable_menu_align()
        # self.update_old_positions_selected_items()

    def update_old_positions_selected_items(self):
        items = self.selected_movable_items()
        if len(items) == 0:
            return

        for item in items:
            item["_OLD_POS"] = item.pos()

        print("update_old_positions_selected_items")
# end of class
