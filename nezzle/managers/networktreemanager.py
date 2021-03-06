
from qtpy.QtCore import Qt
from qtpy.QtCore import QObject
#from qtpy.QtWidgets import QWidget
from qtpy.QtCore import QEvent
from qtpy.QtCore import QVariant
from qtpy.QtCore import Slot
from qtpy.QtCore import QItemSelection
from qtpy.QtCore import QItemSelectionModel
from qtpy.QtCore import QModelIndex
from qtpy.QtGui import QStandardItem
from qtpy.QtGui import QStandardItemModel
from qtpy.QtWidgets import QMenu


class NetworkTreeManager(QObject):

    def __init__(self, mw):
        super().__init__(parent=mw)
        self.mw = mw
        self.tree_view = self.mw.ui_navigationTree
        model = self.mw.nm_manager.model

        self.tree_view.setRootIsDecorated(True)
        self.tree_view.setHeaderHidden(True)
        if model:
            self.tree_view.setModel(model)
            self.tree_view.expandAll()

            selection_model = self.tree_view.selectionModel()
            selection_model.currentChanged.connect(self.on_current_changed)
            selection_model.selectionChanged.connect(self.on_selection_changed)

        self.tree_view.keyPressed.connect(self.keyPressEvent)

        # Create context menu
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.on_context_menu)
        self.pop_menu = QMenu(self.tree_view)

        self.action_open_network = self.pop_menu.addAction('Open Network')
        self.action_save_network = self.pop_menu.addAction('Save Network')
        self.action_remove_selected = self.pop_menu.addAction('Remove Selected')
        self.action_remove_selected.setEnabled(False)

    @property
    def tree_view(self):
        return self._tree_view

    @tree_view.setter
    def tree_view(self, tv):
        self._tree_view = tv

    @property
    def current_item(self):
        # indexes = self.history_view.selectedIndexes()
        # if len(indexes) >= 1:
        #     idx = indexes[-1]
        #     model = self.history_view.model()
        #     item = model.itemFromIndex(idx)
        #     return item

        ind = self.tree_view.currentIndex()
        if ind.row() >= 0:
            model = self.tree_view.model()
            item = model.itemFromIndex(ind)
            return item

        return None

    @property
    def current_net(self):
        item = self.current_item
        if not item:
            return None
        net = item.data()
        return net

    @Slot(QEvent)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.remove_selected_items()

    @Slot(QModelIndex, QModelIndex)
    def on_current_changed(self, current, previous):
        if current.row() < 0:
            self.mw.sv_manager.clear()
            self.mw.ct_manager.update_console_vars()
            return

        model = self.tree_view.model()
        item = model.itemFromIndex(current)
        net = item.data()
        scene = net.scene
        self.action_remove_selected.setEnabled(True)
        self.mw.sv_manager.set_current_view_scene(net.scene, net.name)
        self.mw.ct_manager.update_console_vars()

        self.mw.hv_manager.update_history_view(scene.history)

        # # Process previous net
        # if previous.row() >= 0:
        #     item = model.itemFromIndex(previous)
        #     net = item.data()
        #     scene = net.scene
        #     scene.history.hide_history_view()

    @Slot(QItemSelection, QItemSelection)
    def on_selection_changed(self, selected, deselected):
        self.mw.sv_manager.view.enable_menu_align()

    def append_item(self, net):
        item = QStandardItem(net.name)
        item.setData(QVariant(net))
        model = self.tree_view.model()
        root = model.invisibleRootItem()
        root.appendRow(item)
        net.item = item
        self.tree_view.setCurrentIndex(item.index())
        """
        Following is a code snippet to consult.

        selection_model = self.history_view.selectionModel()
        selection_model.select(item.index(),
                              QItemSelectionModel.ClearAndSelect)
        """

    def clear_selection(self):
        selection_model = self.tree_view.selectionModel()
        selection_model.clear_selection()

    def on_context_menu(self, point):
        action_selected = self.pop_menu.exec_(self.tree_view.mapToGlobal(point))
        if action_selected == self.action_open_network:
            self.mw.ma_handler.process_open_network()
        elif action_selected == self.action_save_network:
            self.mw.ma_handler.process_save_network()
        elif action_selected == self.action_remove_selected:
            self.remove_selected_items()

    def remove_selected_items(self):
        model = self.tree_view.model()
        root = model.invisibleRootItem()
        indexes = self.tree_view.selectedIndexes()

        while len(indexes) > 0:
            ind = indexes[0]
            model.removeRow(ind.row(), ind.parent())
            indexes = self.tree_view.selectedIndexes()

        if root.rowCount() == 0:
            self.mw.sv_manager.clear()
            self.mw.hv_manager.clear()
        else:
            self.on_selection_changed([], [])


    def clear(self):
        self.tree_view.selectAll()
        self.remove_selected_items()