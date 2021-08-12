
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


class NavigationTreeManager(QObject):

    def __init__(self, main_window):
        super().__init__(parent=main_window)
        self.mw = main_window
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
        # indexes = self.tree_view.selectedIndexes()
        # if len(indexes) >= 1:
        #     idx = indexes[-1]
        #     model = self.tree_view.model()
        #     item = model.itemFromIndex(idx)
        #     return item

        ind = self.tree_view.currentIndex()
        if ind.row() >= 0:
            model = self.tree_view.model()
            item = model.itemFromIndex(ind)
            return item

        return None

    @Slot(QEvent)
    def keyPressEvent(self, event):
        print("KeyPressEvent in navigation")
        if event.key() == Qt.Key_Delete:
            self.remove_selected_items()


    @Slot(QModelIndex, QModelIndex)
    def on_current_changed(self, current, previous):
        if current.row()<0:
            self.mw.sv_manager.clear()
            self.mw.ct_manager.update_console_variables()
            return

        #print("current ind: ", current.row())
        model = self.tree_view.model()
        item = model.itemFromIndex(current)
        net = item.data()
        self.action_remove_selected.setEnabled(True)
        self.mw.sv_manager.set_current_view_scene(net.scene, net.name)
        self.mw.ct_manager.update_console_variables()

    @Slot(QItemSelection, QItemSelection)
    def on_selection_changed(self, selected, deselected):
        if selected:
            print("[NAV] selected: ", [ind.row() for ind in selected.indexes()])

        if deselected:
            print("[NAV] deselected: ", [ind.row() for ind in deselected.indexes()])


        self.mw.sv_manager.current_view.enable_menu_align()
        # scene_selected = self.mw.sv_manager.current_view.scene()
        # if len(scene_selected.selectedItems()) > 1:
        #     self.mw.ui_menuAlign.setEnabled(True)
        # else:
        #     self.mw.ui_menuAlign.setEnabled(False)


        #ind_selected = self.tree_view.selectedIndexes()
        # if len(ind_selected) >= 1:
        #     pass
            # idx = ind_selected[-1]
            # model = self.tree_view.model()
            # item = model.itemFromIndex(idx)
            # net = item.data()
            #net = self.current_item.data()
            #ind = self.tree_view.currentIndex()
            #model = self.tree_view.model()
            #item = model.itemFromIndex(ind)
            # print("current ind: ", ind.row())
            # if item:
            #     net = item.data()
            #     self.action_remove_selected.setEnabled(True)
            #     self.mw.sv_manager.set_current_view_scene(net.scene, net.name)
            #     self.mw.ct_manager.update_console_variables()
            #     print("%s is selected."%(net))

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

        selection_model = self.tree_view.selectionModel()
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
        else:
            self.on_selection_changed([], [])
