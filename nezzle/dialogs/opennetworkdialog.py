from qtpy.QtWidgets import QDialog, QFileDialog
from qtpy.QtWidgets import QMessageBox
from qtpy.QtGui import QDoubleValidator
from qtpy.QtCore import Slot
from qtpy.QtCore import Qt

from nezzle.ui.ui_opennetworkdialog import Ui_OpenNetworkDialog
from nezzle.constants import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT


class OpenNetworkDialog(QDialog, Ui_OpenNetworkDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setWindowTitle("Open a network file")
        self.setFixedSize(self.width(), self.height())

        validator_double = QDoubleValidator()
        validator_double.setBottom(0.0)

        self.ui_actSymEdit.setText('+')
        self.ui_inhSymEdit.setText('-')

        self.ui_sceneWidthEdit.setValidator(validator_double)
        self.ui_sceneHeightEdit.setValidator(validator_double)

        self.ui_sceneWidthEdit.setText(str(DEFAULT_SCENE_WIDTH))
        self.ui_sceneHeightEdit.setText(str(DEFAULT_SCENE_HEIGHT))

        self.ui_sceneSizeGroup.setVisible(False)
        # self.ui_sceneWidthEdit.setVisible(False)
        # self.ui_sceneHeightEdit.setVisible(False)
        # self.ui_sceneWidthEdit.setEnabled(False)
        # self.ui_sceneHeightEdit.setEnabled(False)

        self.ui_noLinkTypeCheck.stateChanged.connect(self.on_no_link_type_check)
        self.ui_openButton.released.connect(self.on_open_button_released)
        self.ui_buttonBox.accepted.connect(self.on_accepted)
        self.ui_buttonBox.rejected.connect(self.on_rejected)


    @Slot(int)
    def on_no_link_type_check(self, state):
        if state == Qt.Checked:
            self.ui_actSymEdit.setEnabled(False)
            self.ui_inhSymEdit.setEnabled(False)
        else:
            self.ui_actSymEdit.setEnabled(True)
            self.ui_inhSymEdit.setEnabled(True)

    @Slot()
    def on_open_button_released(self):
        try:
            dialog = QFileDialog(self)
            dialog.setWindowTitle("Open a network file")
            dialog.setAcceptMode(QFileDialog.AcceptOpen)
            dialog.setNameFilters([self.tr("Text files (*.sif *.json)")])
            dialog.setFileMode(QFileDialog.ExistingFile)
            if dialog.exec() == QDialog.Accepted:
                fpath = dialog.selectedFiles()[0]
                self.ui_filePathEdit.setText(fpath)
                fpath = fpath.strip()
                if fpath.endswith('.json'):
                    self.ui_networkNameEdit.setEnabled(False)
                    self.ui_noLinkTypeCheck.setEnabled(False)
                    self.ui_actSymEdit.setEnabled(False)
                    self.ui_inhSymEdit.setEnabled(False)
                    self.ui_sceneWidthEdit.setEnabled(False)
                    self.ui_sceneHeightEdit.setEnabled(False)
                elif fpath.endswith('.sif'):
                    self.ui_networkNameEdit.setEnabled(True)
                    self.ui_noLinkTypeCheck.setEnabled(True)
                    self.ui_actSymEdit.setEnabled(True)
                    self.ui_inhSymEdit.setEnabled(True)
                    self.ui_sceneWidthEdit.setEnabled(True)
                    self.ui_sceneHeightEdit.setEnabled(True)
            # end of if
        except Exception as err:
            print(err)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Open a network file")
            msg.setText("An inappropriate file type for network data.")
            msg.exec()
        # end of except

    @Slot()
    def on_accepted(self):
        self._fpath = self.ui_filePathEdit.text()
        self._network_name = self.ui_networkNameEdit.text()
        self._act_sym = self.ui_actSymEdit.text()
        self._inh_sym = self.ui_inhSymEdit.text()
        self._scene_width = float(self.ui_sceneWidthEdit.text())
        self._scene_height = float(self.ui_sceneWidthEdit.text())
        super().accept()

    @Slot()
    def on_rejected(self):
        self.close()
        super().reject()

    # Read-only properties
    @property
    def fpath(self):
        return self._fpath

    @property
    def network_name(self):
        return self._network_name

    @property
    def act_sym(self):
        return self._act_sym

    @property
    def inh_sym(self):
        return self._inh_sym

    @property
    def scene_width(self):
        return self._scene_width

    @property
    def scene_height(self):
        return self._scene_height

    @property
    def no_link_type(self):
        return self.ui_noLinkTypeCheck.isChecked()

# end of class