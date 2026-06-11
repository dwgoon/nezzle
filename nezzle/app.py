# import warnings
# warnings.filterwarnings("ignore")

import os
from os.path import join as pjoin
import sys
import argparse

from qtpy import QtCore

from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QStyleFactory
from qtpy.QtGui import QIcon, QPixmap

from nezzle.mainwindow import MainWindow

base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)


def _set_windows_app_user_model_id(app_id):
    """Tell Windows this process is its own app, not a generic Python host.

    Without this, the Windows taskbar groups the running window under the
    "python.exe" AUMID and shows the Python icon instead of our window icon.
    Must be called BEFORE QApplication is constructed.
    """
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except (AttributeError, OSError):
        # Older Windows or unusual environment -- silently ignore; the only
        # visible consequence is the wrong taskbar icon.
        pass


def _load_app_icon(resources_dir):
    """Load the app icon at multiple resolutions.

    The shipped ``icon.png`` is a single 256x256 image. Windows requests
    small sizes (16/32 in the taskbar, 48 in alt-tab, etc.) and a one-shot
    auto-scale by Qt can look fuzzy. By pre-rendering each size with
    SmoothTransformation and attaching them all to one QIcon, Qt picks the
    closest match without re-scaling on every paint.

    If ``icon.ico`` exists alongside the PNG, that file is preferred (a
    proper multi-resolution ICO is the ideal format on Windows).
    """
    icon = QIcon()
    ico_path = pjoin(resources_dir, "icon.ico")
    png_path = pjoin(resources_dir, "icon.png")

    if os.path.isfile(ico_path):
        icon.addFile(ico_path)

    if os.path.isfile(png_path):
        base = QPixmap(png_path)
        if not base.isNull():
            for size in (16, 24, 32, 48, 64, 128, 256):
                icon.addPixmap(base.scaled(size, size,
                                            QtCore.Qt.KeepAspectRatio,
                                            QtCore.Qt.SmoothTransformation))
    return icon


def main():
    argparser = argparse.ArgumentParser(description="Nezzle arguments for CUI execution")
    argparser.add_argument('-fc', '--fpath-code',
                           action='store',
                           dest='fpath_code',
                           default=None,
                           help="Designate the absolute file path of a source code file.")
    args = argparser.parse_args()

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    _set_windows_app_user_model_id('com.daewonlee.nezzle')

    libpaths = QApplication.libraryPaths()
    libpaths.append(os.getcwd())
    QApplication.setLibraryPaths(libpaths)

    # High-DPI: scale the whole GUI (fonts, widgets, icons) to the monitor's
    # display scale so text reads the same physical size on a 96-DPI FHD
    # screen and a 150% 4K screen. All of this must run BEFORE QApplication
    # is constructed.
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    try:
        # Qt >= 5.14 rounds the screen scale factor to integers by default
        # (150% -> 200%, 125% -> 100%), which makes fonts visibly too big or
        # too small on fractionally scaled monitors. PassThrough honors the
        # OS setting exactly. (Qt 6 already defaults to PassThrough.)
        from qtpy.QtGui import QGuiApplication
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    except AttributeError:
        pass  # Qt < 5.14: fractional rounding policies not available

    app = QApplication(sys.argv)

    # Unify GUI fonts. Qt 5's default application font on Windows comes from
    # the legacy "MS Shell Dlg 2" alias (Gulim 13pt on Korean systems, Tahoma
    # 8pt on western ones), while menus, dock titles and message boxes get
    # the real system UI font from the platform theme (Malgun Gothic /
    # Segoe UI 9pt). The mix makes group boxes, buttons, labels and tabs
    # render with a visibly different family and size from the rest of the
    # GUI. Adopting the themed message-box font app-wide fixes that, and
    # must happen before MainWindow is built: the embedded console snapshots
    # the default font size at creation.
    app.setFont(QApplication.font("QMessageBox"))

    # It is possible to choose the theme of GUI
    # QApplication.setStyle(QStyleFactory.create("plastique"))

    mw = MainWindow()
    mw.setWindowTitle("Nezzle")
    droot_resources = pjoin(os.path.dirname(__file__), "resources")
    icon = _load_app_icon(droot_resources)
    mw.setWindowIcon(icon)  # for Windows and Linux
    app.setWindowIcon(icon)  # for macOS

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
