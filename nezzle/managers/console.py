from qtpy.QtCore import Qt
from qtpy.QtCore import QObject
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QMenu
from qtpy.QtWidgets import QWidget

from nezzle.widgets.console import ConsoleWidget


class ConsoleTabManager(QObject):
    def __init__(self, mw):
        super().__init__(parent=mw)

        self.mw = mw  # Main Window
        self._tab_widget = self.mw.ui_consoleTabWidget
        self._console_widget = ConsoleWidget(parent=self.tab_widget)

        self.tab_widget.addTab(self.console_widget, "Console")
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setMovable(True)

        #self.tab_widget.tabCloseRequested.connect(self.closeTab)

        # Create context menu
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.on_context_menu)
        self.pop_menu = QMenu(self.tab_widget)
        self.action_restart_console = self.pop_menu.addAction('Restart console')
        #self.appendConsole()

    @property
    def tab_widget(self):
        return self._tab_widget

    @property
    def console_widget(self):
        return self._console_widget

    def restart_console(self):
        self.console_widget.reset()
        self.update_console_vars()

    def update_console_vars(self):
        net = None
        if self.mw.nt_manager.current_item:
            net = self.mw.nt_manager.current_item.data()

        vars = {'net': net,
                'console': self.console_widget,
                'view': self.mw.sv_manager.current_view,
                'nav': self.mw.nt_manager,
                'selected': net.scene.selectedItems()}

        self.console_widget.pushVariables(vars)

    def on_context_menu(self, point):
        action = self.pop_menu.exec_(self.tab_widget.mapToGlobal(point))
        if action == self.action_restart_console:
            self.restart_console()

    # @Slot(int)
    # def closeTab(self, currentIndex):
    #     console_widget = self.widget(currentIndex)
    #     console_widget.stop()
    #     self.removeTab(currentIndex)
