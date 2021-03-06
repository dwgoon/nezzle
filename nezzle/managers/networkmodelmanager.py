from qtpy.QtGui import QStandardItem
from qtpy.QtGui import QStandardItemModel
from qtpy.QtCore import QObject
from qtpy.QtCore import Slot
from qtpy.QtCore import Signal


class NetworkModelManager(QObject):

    def __init__(self, mainWindow, model=None):
        super().__init__()
        self.mw = mainWindow
        if not model:
            model = QStandardItemModel()
            model.setColumnCount(1)

        self._model = model
        self._root = self.model.invisibleRootItem()
        self._model.itemChanged.connect(self.on_item_changed)

    @property
    def model(self):
        return self._model

    @property
    def root(self):
        return self._root

    def on_item_changed(self, item):
        net = item.data()
        if net.name != item.text():
            net.name = item.text()

        if item == self.mw.nt_manager.current_item:
            self.mw.sv_manager.set_current_view_text(net.name)
