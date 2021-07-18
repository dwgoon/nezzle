
from qtpy.QtCore import Qt

from qtpy.QtWidgets import QDialog


from nezzle.ui.ui_progressdialog import Ui_ProgressDialog



class ProgressDialog(QDialog, Ui_ProgressDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setModal(False)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(parent.width()/2,
                         parent.height()/2,
                         self.width(), self.height())

        self._progress_bar = self.ui_progressBar
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(-1)


    def exec(self):
        self._progress_bar.setMaximum(0)
        super().exec()

    def show(self):
        self._progress_bar.setMaximum(0)
        #self.exc(self.nav, self.net)
        super().show()

    def close(self):
        self._progress_bar.setMaximum(100)
        super().close()