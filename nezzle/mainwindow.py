from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMainWindow

from nezzle.ui.ui_mainwindow import Ui_MainWindow
from nezzle.managers.singleviewmanager import SingleViewManager
from nezzle.managers.networktreemanager import NetworkTreeManager
from nezzle.managers.consoletabmanager import ConsoleTabManager
from nezzle.managers.networkmodelmanager import NetworkModelManager
from nezzle.managers.codemanager import CodeManager
from nezzle.managers.historyviewmanager import HistoryViewManager
from nezzle.menu import MenuActionHandler


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)   # GUI parts
        self.ui_visStyleDock.close()

        self.sv_manager = SingleViewManager(self)
        self.nm_manager = NetworkModelManager(self)
        self.nt_manager = NetworkTreeManager(self)
        self.ct_manager = ConsoleTabManager(self)
        self.code_manager = CodeManager(self)
        self.hv_manager = HistoryViewManager(self)

        # The MenuActionHandler object should be created after creating all managers.
        self.ma_handler = MenuActionHandler(self)

        self.setAttribute(Qt.WA_DeleteOnClose)

    # end of __init__

    def closeEvent(self, event):
        self.ct_manager.tab_widget.removeTab(0)
        self.ct_manager.console_widget.stop()
        event.accept()
