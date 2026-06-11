import os
import importlib
import traceback

from qtpy.QtCore import Qt
from qtpy.QtCore import QObject
from qtpy.QtCore import Slot
from qtpy.QtCore import Signal
from qtpy.QtCore import QThread

from qtpy.QtWidgets import QWidget
from qtpy.QtWidgets import QMessageBox
from qtpy.QtWidgets import QDialog, QFileDialog
from qtpy.QtWidgets import QProgressBar

#import nezzle.utils
from nezzle.utils import reload_modules
from nezzle.utils import extract_name_and_ext
from nezzle.utils import get_last_dir
from nezzle.utils import set_last_dir
from nezzle.dialogs.progressdialog import ProgressDialog


class TaskThread(QThread):
    task_finished = Signal()
    def __init__(self, exc, nav, net):
        super().__init__()
        self._exc = exc
        self._nav = nav
        self._net = net

    def run(self):
        self._exc(self._nav, self._net)
        self.task_finished.emit()


class Worker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def set_job(self, func, net):
        self._func_execute = func
        self._net = net

    @Slot()
    def execute(self):
        try:
            nets = self._func_execute(self._net)
        except Exception:
            self.error.emit(traceback.format_exc())
            self.finished.emit(None)
            return
        self.finished.emit(nets)


class CodeManager(QObject):
    def __init__(self, mainWindow):

        super().__init__(mainWindow)

        self.mw = mainWindow
        self._open_button = self.mw.ui_openCodeButton
        self._run_button = self.mw.ui_runButton
        self._file_path_edit = self.mw.ui_codeFilePathEdit

        self._open_button.released.connect(self.on_open_button_released)
        self._run_button.released.connect(self.on_run_button_released)
        self._run_button.setShortcut("Ctrl+R")

        self._worker = Worker()
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._worker.finished.connect(self.on_thread_finished)
        self._worker.error.connect(self.on_worker_error)
        self._thread.started.connect(self._worker.execute)


    @property
    def file_path_edit(self):
        return self._file_path_edit

    def show_exception_message(self, err):
        print(err)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("An error has occurred")
        msg.setText(traceback.format_exc())
        msg.exec()


    @Slot()
    def on_open_button_released(self):
        try:
            dialog = QFileDialog(self.mw)
            dialog.setWindowTitle("Open a Python code")
            dialog.setAcceptMode(QFileDialog.AcceptOpen)
            dialog.setNameFilters([self.tr("Python module files (*.py)")])
            dialog.setFileMode(QFileDialog.ExistingFile)
            dialog.setDirectory(get_last_dir("code"))
            if dialog.exec() == QDialog.Accepted:
                fpath = dialog.selectedFiles()[0]
                fpath = fpath.strip()
                if not fpath.endswith('.py'):
                    raise RuntimeError("An inappropriate file "
                                       "for Python code: %s"%(fpath))
                # end of if
                set_last_dir("code", fpath)
                self._file_path_edit.setText(fpath)
            # end of if
        except Exception as err:
            self.show_exception_message(err)

    @Slot()
    def on_run_button_released(self):
        try:
            self.process_code(self.file_path_edit.text())
        except Exception as err:
            self.show_exception_message(err)


    @Slot(str)
    def on_worker_error(self, err):
        print(err)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("An error has occurred")
        msg.setText(err)
        msg.exec()

    @Slot(object)
    def on_thread_finished(self, nets):
        self._thread.quit()
        self._thread.wait()
        if nets:
            if not isinstance(nets, (list, tuple)):
                nets = [nets]
            try:
                for net in nets:
                    self.mw.nt_manager.append_item(net.copy())
            except Exception as err:
                self.show_exception_message(err)

    def process_code(self, fpath):
        if self._thread.isRunning():
            raise RuntimeError("A previous code execution is still running.")

        fname, fext = extract_name_and_ext(fpath)

        if not fname:
            raise RuntimeError("The path for the Python module is not valid.")

        # [REF] https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        spec = importlib.util.spec_from_file_location(fname, fpath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        if self.mw.nt_manager.current_item:
            net = self.mw.nt_manager.current_item.data()
        else:
            net = None

        if hasattr(mod, 'create'):
            self._worker.set_job(mod.create, net.copy() if net is not None else None)
            self._thread.start()

        if hasattr(mod, 'update'):
            mod.update(self.mw.nt_manager, net)



