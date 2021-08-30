from qtpy.QtCore import Qt
from qtpy.QtCore import Signal
from qtpy.QtCore import QObject
from qtpy.QtCore import QItemSelection
from qtpy.QtWidgets import QUndoView
from qtpy.QtWidgets import QUndoStack


class HistoryView(QUndoView):
    itemSelectionChanged = Signal(QItemSelection, QItemSelection)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("History")
