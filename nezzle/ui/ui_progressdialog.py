# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './nezzle/ui/ui_progressdialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        ProgressDialog.setObjectName("ProgressDialog")
        ProgressDialog.resize(449, 40)
        ProgressDialog.setSizeGripEnabled(False)
        ProgressDialog.setModal(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(ProgressDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ui_progressBar = QtWidgets.QProgressBar(ProgressDialog)
        self.ui_progressBar.setProperty("value", 0)
        self.ui_progressBar.setTextVisible(False)
        self.ui_progressBar.setObjectName("ui_progressBar")
        self.verticalLayout.addWidget(self.ui_progressBar)

        self.retranslateUi(ProgressDialog)
        QtCore.QMetaObject.connectSlotsByName(ProgressDialog)

    def retranslateUi(self, ProgressDialog):
        _translate = QtCore.QCoreApplication.translate
        ProgressDialog.setWindowTitle(_translate("ProgressDialog", "Dialog"))

