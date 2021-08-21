import os

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QFileDialog
from qtpy.QtWidgets import QMessageBox
from qtpy.QtGui import QDoubleValidator
from qtpy.QtGui import QIntValidator
from qtpy.QtCore import Slot

from nezzle.ui.ui_exportimagedialog import Ui_ExportImageDialog
from nezzle.utils import extract_name_and_ext
#from nezzle.constants import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT

class ExportImageDialog(QDialog, Ui_ExportImageDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setWindowTitle("Export an image")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setFixedSize(self.width(), self.height())

        validator_int_percent = QIntValidator(0, 100)
        validator_int_nonnegative = QIntValidator()
        validator_int_nonnegative.setBottom(0)

        #validator_double_nonnegative = QDoubleValidator()
        #validator_double_nonnegative.setBottom(0.0)

        # Set the bounds of quality slider
        self.ui_qualitySlider.setMinimum(0)
        self.ui_qualitySlider.setMaximum(100)

        # Set validators
        self.ui_qualityEdit.setValidator(validator_int_percent)

        self.ui_scaleWidthEdit.setValidator(validator_int_nonnegative)
        self.ui_scaleHeightEdit.setValidator(validator_int_nonnegative)

        self.ui_dpiWidthEdit.setValidator(validator_int_nonnegative)
        self.ui_dpiHeightEdit.setValidator(validator_int_nonnegative)

        # Set default values
        self.ui_transparencyCheck.setChecked(True)

        self.ui_qualitySlider.setValue(100)
        self.ui_qualityEdit.setText('100')

        self.ui_scaleWidthEdit.setText('200')
        self.ui_scaleHeightEdit.setText('200')

        self.ui_dpiWidthEdit.setText('350')
        self.ui_dpiHeightEdit.setText('350')

        # Connect signal and slot
        self.ui_openButton.released.connect(self.onOpenButtonReleased)

        self.ui_qualitySlider.valueChanged.connect(self.onQualitySliderValueChanged)
        self.ui_qualityEdit.textChanged.connect(self.onQualityEditTextChanged)

        self.ui_buttonBox.accepted.connect(self.onAccepted)
        self.ui_buttonBox.rejected.connect(self.onRejected)


    @Slot()
    def onOpenButtonReleased(self):
        try:
            fpath = QFileDialog.getSaveFileName(self,
                                                self.tr("Save an image"),
                                                "",
                                                self.tr("Image files (*.png *.jpeg)"))

            fpath = fpath[0]
            if fpath:
                self.ui_filePathEdit.setText(fpath)
                fname, fext = extract_name_and_ext(fpath)
                if fext.casefold() in ['jpeg']:
                    self.ui_transparencyCheck.setEnabled(False)
                else:
                    self.ui_transparencyCheck.setEnabled(True)


            # end of if
        except Exception as err:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Open a network file")
            msg.setText("An invalid file type for image.")
            msg.exec()
        # end of except

    @Slot()
    def onAccepted(self):
        self._fpath = self.ui_filePathEdit.text()
        self._isTransparent = self.ui_transparencyCheck.isChecked()

        try:
            self._quality = int(self.ui_qualitySlider.value())
        except ValueError:
            self._quality = 100
            self.ui_qualitySlider.setValue(100)
            self.ui_qualityEdit.setText('100')

        try:
            self._scaleWidth = int(self.ui_scaleWidthEdit.text())
        except ValueError:
            self._scaleWidth = 100

        try:
            self._scaleHeight = int(self.ui_scaleWidthEdit.text())
        except ValueError:
            self._scaleHeight = 100


        try:
            self._dpiWidth = int(self.ui_dpiWidthEdit.text())
        except ValueError:
            self._dpiWidth = 350

        try:
            self._dpiHeight = int(self.ui_dpiHeightEdit.text())
        except ValueError:
            self._dpiHeight = 350

        super().accept()

    @Slot()
    def onQualitySliderValueChanged(self):
        self.ui_qualityEdit.setText(str(self.ui_qualitySlider.value()))

    @Slot()
    def onQualityEditTextChanged(self):
        if self.ui_qualityEdit.text():
            self.ui_qualitySlider.setValue(int(self.ui_qualityEdit.text()))
        else:
            self.ui_qualitySlider.setValue(0)

    @Slot()
    def onRejected(self):
        self.close()
        super().reject()


    # Read-only properties
    @property
    def fpath(self):
        return self._fpath

    @property
    def isTransparent(self):
        return self._isTransparent

    @property
    def quality(self):
        return self._quality

    @property
    def scaleWidth(self):
        return self._scaleWidth

    @property
    def scaleHeight(self):
        return self._scaleHeight

    @property
    def dpiWidth(self):
        return self._dpiWidth

    @property
    def dpiHeight(self):
        return self._dpiHeight



# end of class