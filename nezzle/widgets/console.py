# [REF] http://stackoverflow.com/a/41070191

from qtpy.QtCore import Qt
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QMenu
from qtpy.QtWidgets import QTabWidget

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager


class ConsoleWidget(RichJupyterWidget):

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)

        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel(show_banner=False)
        self.kernel_manager.kernel.gui = 'qt'
        self.kernel_manager.kernel.shell.cache_size = 50000

        def _abort_queues(kernel):
            pass

        self.kernel_manager.kernel._abort_queues = _abort_queues
        
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()

        self.buffer_size = 1000
        self.exit_requested.connect(self.stop)

        self.setAttribute(Qt.WA_DeleteOnClose)


    @Slot()
    def stop(self):
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()

        self.close()
        self.deleteLater()


    def pushVariables(self, variableDict):
        """
        Given a dictionary containing labels / value pairs, push those variables
        to the Jupyter console widget
        """
        self.kernel_manager.kernel.shell.push(variableDict)

    def clear(self):
        """
        Clears the terminal
        """
        
        self._control.clear()

    def printText(self, text):
        """
        Prints some plain text to the console
        """
        self._append_plain_text(text)

    def executeCommand(self, command):
        """
        Execute a command in the frame of the console widget
        """
        self._execute(command, False)
        
    def reset(self, clear=True):
        super().reset(clear)


class ConsoleTabWidget(QTabWidget):

        def __init__(self, *args, **kwargs):
        
            super().__init__(*args, **kwargs)
            self.setTabsClosable(True)
            self.setMovable(True)
            
            self.tabCloseRequested.connect(self.closeTab)
                        
            # Set button context menu policy
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.onContextMenu)

            # Create context menu
            self.pop_menu = QMenu(self)
            self.actionNewConsole = self.pop_menu.addAction('New console')
            self.appendConsole()
            
        def appendConsole(self):            
            console = ConsoleWidget()
            self.addTab(console, "Console")
            console.pushVariables({'console': console})

        @Slot()
        def onContextMenu(self, point):
            if self.count() == 1:
                self.actionNewConsole.setEnabled(False)
            elif self.count() == 0:
                self.actionNewConsole.setEnabled(True)
            else:
                raise RuntimeError("An illegal state of the ConsoleTabWidget object "
                                    "has been detected.")
            
            selectedAction = self.pop_menu.exec_(self.mapToGlobal(point))
            if selectedAction == self.actionNewConsole:
                self.appendConsole()                
                
            
        @Slot(int)
        def closeTab(self, currentIndex):   
            consoleWidget = self.widget(currentIndex)
            consoleWidget.stop()
            self.removeTab(currentIndex)
