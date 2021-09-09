
from qtpy.QtCore import Qt
from qtpy.QtCore import Signal
from qtpy.QtCore import QEvent
from qtpy.QtWidgets import QTreeView


class NetworkTreeView(QTreeView):
    keyPressed = Signal(QEvent)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.keyPressed.emit(event)