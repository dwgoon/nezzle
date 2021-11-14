# import warnings
# warnings.filterwarnings("ignore")

import os
from os.path import join as pjoin
import sys
import argparse

from qtpy import QtCore

from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QStyleFactory
from qtpy.QtGui import QIcon

from nezzle.mainwindow import MainWindow

base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)


def main():
    argparser = argparse.ArgumentParser(description="Nezzle arguments for CUI execution")
    argparser.add_argument('-fc', '--fpath-code',
                           action='store',
                           dest='fpath_code',
                           default=None,
                           help="Designate the absolute file path of a source code file.")
    args = argparser.parse_args()

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    libpaths = QApplication.libraryPaths()
    libpaths.append(os.getcwd())
    QApplication.setLibraryPaths(libpaths)
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QApplication(sys.argv)

    # It is possible to choose the theme of GUI
    # QApplication.setStyle(QStyleFactory.create("plastique"))

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


if __name__ == "__main__":
    main()
