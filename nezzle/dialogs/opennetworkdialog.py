from qtpy.QtCore import Slot
from qtpy.QtCore import Qt
from qtpy.QtGui import QDoubleValidator
from qtpy.QtWidgets import QDialog, QFileDialog
from qtpy.QtWidgets import QMessageBox
from qtpy.QtWidgets import QTableWidgetItem
from qtpy.QtWidgets import QComboBox

from nezzle.ui.ui_opennetworkdialog import Ui_OpenNetworkDialog
from nezzle.io import read_metadata
from nezzle.graphics.arrows.arrowclassfactory import ArrowClassFactory


class OpenNetworkDialog(QDialog, Ui_OpenNetworkDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setWindowTitle("Open a network file")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        validator_double = QDoubleValidator()
        validator_double.setBottom(0.0)

        # Set TableWidget for edge haader mapping
        self.ui_edgeHeadMappingTable.setColumnCount(3)
        self.ui_edgeHeadMappingTable.setHorizontalHeaderLabels(["Count", "Interaction", "Head"])

        # Set head selection QComboBox
        self._available_heads = ArrowClassFactory.get_available_heads()
        self._head_selections = {}

        # Edge signal and slot
        self.ui_openButton.released.connect(self.on_open_button_released)
        self.ui_reloadButton.released.connect(self.on_reload_button_released)
        self.ui_buttonBox.accepted.connect(self.on_accepted)
        self.ui_buttonBox.rejected.connect(self.on_rejected)

        # TODO: Implement tail mapping
        self.ui_edgeTailMappingTable.setColumnCount(3)
        self.ui_edgeTailMappingTable.setHorizontalHeaderLabels(["Count", "Interaction", "Tail"])
        self.ui_edgeTailMappingTable.setItem(0, 0, QTableWidgetItem("Currently Not Supported"))

        self.ui_edgeTailMappingTable.setDisabled(True)

    @Slot()
    def on_open_button_released(self):
        try:
            dialog = QFileDialog(self)
            dialog.setWindowTitle("Open a network file")
            dialog.setAcceptMode(QFileDialog.AcceptOpen)
            dialog.setNameFilters([self.tr("Text files (*.sif *.cx *.nzj *.json)")])
            dialog.setFileMode(QFileDialog.ExistingFile)
            if dialog.exec() == QDialog.Accepted:
                fpath = dialog.selectedFiles()[0]
                self.ui_filePathEdit.setText(fpath)
                self.on_reload_button_released()
            # end of if
        except Exception as err:
            print(err)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Open a network file")
            msg.setText("Invalid file type or file contents!")
            msg.exec()
        # end of except

    @Slot()
    def on_reload_button_released(self):
        fpath = self.ui_filePathEdit.text()
        fpath = fpath.strip()

        if not fpath or len(fpath) <= 0:
            return

        self._head_selections.clear()
        metadata = read_metadata(fpath)
        interactions = metadata["INTERACTIONS"]
        num_rows = len(interactions)
        self.ui_edgeHeadMappingTable.setRowCount(num_rows)
        for i, (interaction_name, count) in enumerate(interactions.items()):
            # Column (0): Count of each interaction
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            count_item.setFlags(count_item.flags() ^ Qt.ItemIsEditable)
            self.ui_edgeHeadMappingTable.setItem(i, 0, count_item)

            # Column (1): Interaction name
            interaction_item = QTableWidgetItem(interaction_name)
            interaction_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            count_item.setFlags(count_item.flags() ^ Qt.ItemIsEditable)
            self.ui_edgeHeadMappingTable.setItem(i, 1, interaction_item)

            # Column (2): QComboBox for selecting heads
            cb = QComboBox()
            cb.addItems(self._available_heads)
            if interaction_name in self._available_heads:
                index = self._available_heads.index(interaction_name)
                cb.setCurrentIndex(index)

            self.ui_edgeHeadMappingTable.setCellWidget(i, 2, cb)
            self._head_selections[interaction_name] = cb
        # end of for

        self.ui_networkNameEdit.setText(metadata["NETWORK_NAME"])

    @Slot()
    def on_accepted(self):
        self._fpath = self.ui_filePathEdit.text()
        self._network_name = self.ui_networkNameEdit.text().strip()
        super().accept()

    @Slot()
    def on_rejected(self):
        self.close()
        super().reject()

    # Read-only properties
    @property
    def edge_map(self):
        _edge_map = {}
        for interaction_name, cb in self._head_selections.items():
            _edge_map[interaction_name] = cb.currentText()
        return _edge_map

    @property
    def fpath(self):
        return self._fpath

    @property
    def network_name(self):
        return self._network_name

    # @property
    # def act_sym(self):
    #     return self._act_sym
    #
    # @property
    # def inh_sym(self):
    #     return self._inh_sym

    # @property
    # def scene_width(self):
    #     return self._scene_width
    #
    # @property
    # def scene_height(self):
    #     return self._scene_height

    @property
    def no_edge_type(self):
        return self.ui_noEdgeTypeCheck.isChecked()
# end of class