
__author__ = "Daewon Lee"
__copyright__ = "Copyright 2021, Daewon Lee"
__credits__ = ["Daewon Lee", ]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Daewon Lee (daewon4you@gmail.com)"
__email__ = "daewon4you@gmail.com"
__status__ = "Production"

# import warnings
# warnings.filterwarnings("ignore")

import os
from os.path import join as pjoin
import sys

from qtpy import QtWidgets
from qtpy.QtWidgets import QStyleFactory
from qtpy.QtGui import QIcon
from qtpy.QtCore import QFileInfo, QSize

from nezzle.mainwindow import MainWindow


base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)

def main():
    libpaths = QtWidgets.QApplication.libraryPaths()
    libpaths.append(os.getcwd())
    #libpaths.append("C:/Users/dwlee/Envs/calc/Lib/site-packages/qtpy/Qt/plugins")
    QtWidgets.QApplication.setLibraryPaths(libpaths)

    app = QtWidgets.QApplication(sys.argv)

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

    mw.show()

    sys.exit(app.exec())

    
if __name__ == "__main__":
    main()