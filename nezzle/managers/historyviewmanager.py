from qtpy.QtCore import Qt
from qtpy.QtCore import QObject

from nezzle.widgets.historyview import HistoryView


class HistoryViewManager(QObject):

    def __init__(self, mw):
        super().__init__(parent=mw)
        self.mw = mw
        self._history = None
        self._history_view = self.mw.ui_historyView

        selection_model = self.history_view.selectionModel()
        selection_model.selectionChanged.connect(self.on_selection_changed)

    @property
    def history_view(self):
        return self._history_view

    @history_view.setter
    def history_view(self, view):
        if not isinstance(view, HistoryView):
            raise TypeError("%s is not HistoryView instance"%(view))

        self._history_view = view

    @property
    def stack(self):
        return self._history.stack

    @property
    def history(self):
        return self._history

    def update_history_view(self, history):
        self._history = history
        self.history_view.setStack(history.stack)

    def on_selection_changed(self, current, previous):
        model_index = current.indexes()[0]  # Get QModelIndex from QItemSelection
        scene = self.mw.sv_manager.current_scene
        selected = scene.selectedItems()

    def clear(self):
        if self._history:
            try:
                self._history.stack.clear()
            except RuntimeError as err:
                print(id(self._history.stack))
                print(err)