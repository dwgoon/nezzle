# -*- coding: utf-8 -*-


from qtpy.QtWidgets import QMainWindow


from nezzle.managers.view import SingleViewManager
from nezzle.managers.navigation import NavigationTreeManager
from nezzle.managers.console import ConsoleTabManager
from nezzle.managers.networkmodel import NetworkModelManager
from nezzle.managers.code import CodeManager
from nezzle.menu import MenuActionHandler
from nezzle.ui.ui_mainwindow import Ui_MainWindow



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)   # GUI parts
        self.ui_visStyleDock.close()

        self.ma_handler = MenuActionHandler(self)
        self.sv_manager = SingleViewManager(self)
        self.nm_manager = NetworkModelManager(self)
        self.nt_manager = NavigationTreeManager(self)
        self.ct_manager = ConsoleTabManager(self)
        self.code_manager = CodeManager(self)

    # end of __init__



    def closeEvent(self, event):
        print("Quit event")
        self.ct_manager.tab_widget.removeTab(0)
        self.ct_manager.console_widget.stop()
        event.accept()
        # reply = QMessageBox.question(self,
        #                              "Exit the program",
        #                              "Are you sure to quit?",
        #                              QMessageBox.Yes, QMessageBox.No)
        #
        # if reply == QMessageBox.Yes:
        #     self.ct_manager.console_widget.stop()
        #     event.accept()
        # else:
        #     event.ignore()
