# [REF] http://stackoverflow.com/a/41070191

import os
import sys
import tornado


from threading import Thread

from IPython import get_ipython
from ipykernel.kernelapp import IPKernelApp

from qtpy.QtCore import QObject
from qtpy import QtCore
from qtpy.QtCore import Slot, Signal
from qtpy.QtWidgets import QMenu
from qtpy.QtWidgets import QAction
from qtpy.QtWidgets import QTabWidget
from qtpy.QtCore import QThread

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from qtconsole import console_widget


# def background(f):
#     """
#     Call a function in a simple thread, to prevent blocking
#
#     Taken from the Jupyter Qtconsole project
#     """
#     t = Thread(target=f)
#     t.start()
#     return t


class ConsoleWidget(RichJupyterWidget):

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)

        # if banner:
        #     self.banner = banner
        #     self.font_size = 12

        #self.kernel_manager = QtKernelManager(config=None, autorestart=True)
        self.kernel_manager = QtInProcessKernelManager()
        #self.kernel_manager.load_connection_file()
        self.kernel_manager.start_kernel(show_banner=False)
        self.kernel_manager.kernel.gui = 'qt'
        #kernel_manager.kernel.shell.cache_size = 10

        def _abort_queues(kernel):
            pass

        self.kernel_manager.kernel._abort_queues = _abort_queues
        
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()
        #self.kernel_client.execute(code="print('Hello~!')")
        #kernel_app = default_kernel_app()


        self.buffer_size = 1000



        self.exit_requested.connect(self.stop)



    @Slot()
    def stop(self):
        #background(self.kernel_client.stop_channels)
        #background(self.kernel_manager.shutdown_kernel)

        #QtCore.QTimer.singleShot(0, self.kernel_client.stop_channels)
        #QtCore.QTimer.singleShot(0, self.kernel_manager.shutdown_kernel)

        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()

        self.close()
        self.deleteLater()


    def pushVariables(self, variableDict):
        """
        Given a dictionary containing labels / value pairs, push those variables
        to the Jupyter console widget
        """

        #self.kernel_client.execute(code, silent=True)
        self.kernel_manager.kernel.shell.push(variableDict)

    def clear(self):
        """
        Clears the terminal
        """
        
        self._control.clear()
        # self.kernel_manager

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
                        
            # set button context menu policy
            self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.onContextMenu)

            # create context menu
            self.popMenu = QMenu(self)
            self.actionNewConsole = self.popMenu.addAction('New console')
            self.appendConsole()
            
        def appendConsole(self):            
            console = ConsoleWidget(banner="<<< Signal Flow Visualization >>>\n")
            self.addTab(console, "Console")
            console.pushVariables({'console': console})

        @Slot()
        def onContextMenu(self, point):
            print("Num. of console tabs: ", self.count())
            if self.count() == 1:
                self.actionNewConsole.setEnabled(False)
            elif self.count() == 0:
                self.actionNewConsole.setEnabled(True)
            else:
                raise RuntimeError("An illegal state of the ConsoleTabWidget object "
                                    "has been detected.")
            
            selectedAction = self.popMenu.exec_(self.mapToGlobal(point))
            if selectedAction == self.actionNewConsole:
                self.appendConsole()                
                
            
        @Slot(int)
        def closeTab(self, currentIndex):   
            consoleWidget = self.widget(currentIndex)
            consoleWidget.stop()
            self.removeTab(currentIndex)
