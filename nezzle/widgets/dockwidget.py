from qtpy.QtCore import Signal
from qtpy.QtWidgets import QDockWidget


class DockWidget(QDockWidget):
    closeEventOccured = Signal(bool)

    def closeEvent(self, event):
        self.closeEventOccured.emit(False)
        return super().closeEvent(event)
