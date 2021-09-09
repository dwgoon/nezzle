# import warnings
# warnings.filterwarnings("ignore")

import os
from os.path import join as pjoin
import sys

from qtpy import QtCore
from qtpy.QtCore import QFile
from qtpy.QtCore import QTextStream
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
    #libpaths.append(".../site-packages/qtpy/Qt/plugins")
    QtWidgets.QApplication.setLibraryPaths(libpaths)

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    # It is possible to choose the theme of GUI
    #QtWidgets.QApplication.setStyle(QStyleFactory.create("plastique"))

    mw = MainWindow()
    mw.setWindowTitle("Nezzle")
    droot_resources = pjoin(os.path.dirname(__file__), "resources")
    icon = QIcon(pjoin(droot_resources, "icon.png"))
    mw.setWindowIcon(icon)

    # Before showing the main window, process arguments.
    if args:
        if not args.fpath_code:
            pass
        elif os.path.isfile(args.fpath_code):
                mw.code_manager.process_code(args.fpath_code)
                mw.code_manager.file_path_edit.setText(args.fpath_code)
        else:
            sys.stderr.write("File path of source code is not valid: %s\n"%(args.fpath_code))

    # Show the main window.
    mw.show()

    sys.exit(app.exec())

    
