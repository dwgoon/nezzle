# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './nezzle/ui/ui_opennetworkdialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_OpenNetworkDialog(object):
    def setupUi(self, OpenNetworkDialog):
        OpenNetworkDialog.setObjectName("OpenNetworkDialog")
        OpenNetworkDialog.resize(591, 470)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(OpenNetworkDialog.sizePolicy().hasHeightForWidth())
        OpenNetworkDialog.setSizePolicy(sizePolicy)
        OpenNetworkDialog.setWindowOpacity(2.0)
        OpenNetworkDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(OpenNetworkDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_fpath = QtWidgets.QLabel(OpenNetworkDialog)
        self.label_fpath.setObjectName("label_fpath")
        self.horizontalLayout.addWidget(self.label_fpath)
        self.ui_filePathEdit = QtWidgets.QLineEdit(OpenNetworkDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_filePathEdit.sizePolicy().hasHeightForWidth())
        self.ui_filePathEdit.setSizePolicy(sizePolicy)
        self.ui_filePathEdit.setObjectName("ui_filePathEdit")
        self.horizontalLayout.addWidget(self.ui_filePathEdit)
        self.ui_openButton = QtWidgets.QPushButton(OpenNetworkDialog)
        self.ui_openButton.setObjectName("ui_openButton")
        self.horizontalLayout.addWidget(self.ui_openButton)
        self.ui_reloadButton = QtWidgets.QPushButton(OpenNetworkDialog)
        self.ui_reloadButton.setObjectName("ui_reloadButton")
        self.horizontalLayout.addWidget(self.ui_reloadButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_network_name = QtWidgets.QLabel(OpenNetworkDialog)
        self.label_network_name.setObjectName("label_network_name")
        self.horizontalLayout_2.addWidget(self.label_network_name)
        self.ui_networkNameEdit = QtWidgets.QLineEdit(OpenNetworkDialog)
        self.ui_networkNameEdit.setObjectName("ui_networkNameEdit")
        self.horizontalLayout_2.addWidget(self.ui_networkNameEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.ui_labelEdgeHeadMapping = QtWidgets.QLabel(OpenNetworkDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_labelEdgeHeadMapping.sizePolicy().hasHeightForWidth())
        self.ui_labelEdgeHeadMapping.setSizePolicy(sizePolicy)
        self.ui_labelEdgeHeadMapping.setObjectName("ui_labelEdgeHeadMapping")
        self.verticalLayout.addWidget(self.ui_labelEdgeHeadMapping)
        self.ui_edgeHeadMappingTable = QtWidgets.QTableWidget(OpenNetworkDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_edgeHeadMappingTable.sizePolicy().hasHeightForWidth())
        self.ui_edgeHeadMappingTable.setSizePolicy(sizePolicy)
        self.ui_edgeHeadMappingTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.ui_edgeHeadMappingTable.setAlternatingRowColors(True)
        self.ui_edgeHeadMappingTable.setObjectName("ui_edgeHeadMappingTable")
        self.ui_edgeHeadMappingTable.setColumnCount(0)
        self.ui_edgeHeadMappingTable.setRowCount(0)
        self.ui_edgeHeadMappingTable.horizontalHeader().setCascadingSectionResizes(False)
        self.verticalLayout.addWidget(self.ui_edgeHeadMappingTable)
        self.ui_labelEdgeTailMapping = QtWidgets.QLabel(OpenNetworkDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_labelEdgeTailMapping.sizePolicy().hasHeightForWidth())
        self.ui_labelEdgeTailMapping.setSizePolicy(sizePolicy)
        self.ui_labelEdgeTailMapping.setObjectName("ui_labelEdgeTailMapping")
        self.verticalLayout.addWidget(self.ui_labelEdgeTailMapping)
        self.ui_edgeTailMappingTable = QtWidgets.QTableWidget(OpenNetworkDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_edgeTailMappingTable.sizePolicy().hasHeightForWidth())
        self.ui_edgeTailMappingTable.setSizePolicy(sizePolicy)
        self.ui_edgeTailMappingTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.ui_edgeTailMappingTable.setAlternatingRowColors(True)
        self.ui_edgeTailMappingTable.setObjectName("ui_edgeTailMappingTable")
        self.ui_edgeTailMappingTable.setColumnCount(0)
        self.ui_edgeTailMappingTable.setRowCount(0)
        self.ui_edgeTailMappingTable.horizontalHeader().setCascadingSectionResizes(False)
        self.verticalLayout.addWidget(self.ui_edgeTailMappingTable)
        self.ui_buttonBox = QtWidgets.QDialogButtonBox(OpenNetworkDialog)
        self.ui_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.ui_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.ui_buttonBox.setObjectName("ui_buttonBox")
        self.verticalLayout.addWidget(self.ui_buttonBox)

        self.retranslateUi(OpenNetworkDialog)
        self.ui_buttonBox.accepted.connect(OpenNetworkDialog.accept)
        self.ui_buttonBox.rejected.connect(OpenNetworkDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(OpenNetworkDialog)

    def retranslateUi(self, OpenNetworkDialog):
        _translate = QtCore.QCoreApplication.translate
        OpenNetworkDialog.setWindowTitle(_translate("OpenNetworkDialog", "Dialog"))
        self.label_fpath.setText(_translate("OpenNetworkDialog", "File Path"))
        self.ui_openButton.setText(_translate("OpenNetworkDialog", "Open"))
        self.ui_reloadButton.setText(_translate("OpenNetworkDialog", "Reload"))
        self.label_network_name.setText(_translate("OpenNetworkDialog", "Network Name"))
        self.ui_labelEdgeHeadMapping.setText(_translate("OpenNetworkDialog", "Edge Head Mapping"))
        self.ui_edgeHeadMappingTable.setSortingEnabled(True)
        self.ui_labelEdgeTailMapping.setText(_translate("OpenNetworkDialog", "Edge Tail Mapping"))
        self.ui_edgeTailMappingTable.setSortingEnabled(True)
