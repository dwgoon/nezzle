from qtpy.QtCore import Slot
from qtpy.QtCore import QObject
from qtpy.QtWidgets import QUndoView
from qtpy.QtWidgets import QUndoStack
from qtpy.QtGui import QKeySequence

from nezzle.command.commands import MoveByMouseCommand
from nezzle.command.commands import MoveByKeyCommand


class History(QObject):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.undo_stack = QUndoStack(self)

    def on_items_moved_by_mouse(self, items):
         self.undo_stack.push(MoveByMouseCommand(items))

    def on_items_moved_by_key(self, items):
        self.undo_stack.push(MoveByKeyCommand(items))

    def undo(self):
        self.undo_stack.undo()

    def redo(self):
        self.undo_stack.redo()
