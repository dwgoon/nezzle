# import warnings
# warnings.filterwarnings("ignore")

import os
from os.path import join as pjoin
import sys

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy.QtWidgets import QStyleFactory
from qtpy.QtGui import QIcon
from qtpy.QtCore import QFileInfo, QSize

from nezzle.mainwindow import MainWindow

base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)

def main(args=None):
    libpaths = QtWidgets.QApplication.libraryPaths()
    libpaths.append(os.getcwd())
    #libpaths.append("C:/Users/dwlee/Envs/calc/Lib/site-packages/qtpy/Qt/plugins")
    QtWidgets.QApplication.setLibraryPaths(libpaths)

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    # It is possible to choose the theme of GUI
    QtWidgets.QApplication.setStyle(QStyleFactory.create("plastique"))

    mw = MainWindow()
    
    mw.setWindowTitle("Nezzle")
    #dpath = QFileInfo(__file__).absolutePath()
    droot_resources = pjoin(os.path.dirname(__file__), "resources")
    print(droot_resources)
    
    icon = QIcon(pjoin(droot_resources, "icon.png"))
    # icon.addFile(pjoin(droot_resources, "icon16x16.png"), QSize(16, 16))
    # icon.addFile(pjoin(droot_resources, "icon24x24.png"), QSize(24, 24))
    # icon.addFile(pjoin(droot_resources, "icon32x32.png"), QSize(32, 32))
    # icon.addFile(pjoin(droot_resources, "icon48x48.png"), QSize(48, 48))
    # icon.addFile(pjoin(droot_resources, "icon256x256.png"), QSize(256, 256))
        
    print(icon.isNull())
    print(icon.name(), icon.themeName())
    mw.setWindowIcon(icon)

    # Before showing the main window, process arguments.

    if args:
        if not args.fpath_code:
            pass
        elif os.path.isfile(args.fpath_code):
                mw.code_manager.process_code(args.fpath_code)
                print("%s has been executed."%(args.fpath_code))
                mw.code_manager.file_path_edit.setText(args.fpath_code)
        else:
            sys.stderr.write("Network file is not valid: %s\n"%(args.fpath_code))


    # Show the main window.
    mw.show()

    sys.exit(app.exec())

    
