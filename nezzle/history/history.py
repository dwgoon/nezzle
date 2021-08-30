from qtpy.QtCore import Qt
from qtpy.QtCore import QObject
from qtpy.QtWidgets import QUndoView
from qtpy.QtWidgets import QUndoStack
from qtpy.QtGui import QKeySequence

from nezzle.history.commands import MoveByMouseCommand
from nezzle.history.commands import MoveByKeyCommand
from nezzle.history.commands import ConvertNodeCommand
from nezzle.history.commands import ConvertLinkCommand


class History(QObject):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self._undo_stack = QUndoStack(self)

    def on_move_items_by_mouse(self, items):
        self._undo_stack.push(MoveByMouseCommand(items))

    def on_move_items_by_key(self, items):
        self._undo_stack.push(MoveByKeyCommand(items))

    def on_convert_links(self, net, old_items, new_items):
        self._undo_stack.push(ConvertLinkCommand(net, old_items, new_items))

    def on_convert_nodes(self, net, old_items, new_items):
        self._undo_stack.push(ConvertNodeCommand(net, old_items, new_items))

    def undo(self):
        self._undo_stack.undo()

    def redo(self):
        self._undo_stack.redo()

    @property
    def stack(self):
        return self._undo_stack

    # def show_history_view(self):
    #     self.undo_view.show()
    #
    # def hide_history_view(self):
    #     self.undo_view.hide()