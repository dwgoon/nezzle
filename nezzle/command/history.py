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
        #self.mw = mw  # Main Window
        self.undo_stack = QUndoStack(self)

        # self.mw.ui_actionUndo = self.undo_stack.createUndoAction(self, "&Undo")
        # self.mw.ui_actionUndo.setShortcuts(QKeySequence.Undo)
        #
        # self.mw.ui_actionRedo = self.undo_stack.createRedoAction(self, "&Redo")
        # self.mw.ui_actionRedo.setShortcuts(QKeySequence.Redo)

        #self.mw.ui_menuEdit.insertAction(self.mw.ui_actionCopy, self.mw.ui_actionRedo)
        #self.mw.ui_menuEdit.insertAction(self.mw.ui_actionRedo, self.mw.ui_actionUndo)
        #self.mw.ui_menuEdit.insertSeparator(self.mw.ui_actionCopy)


        #self.mw.ui_actionUndo.triggered.connect(self.process_undo)
        #self.mw.ui_actionRedo.triggered.connect(self.process_redo)

    # @Slot(list, list)
    # def on_items_moved(self, items, old_positions):
    #      self.undo_stack.push(MoveCommand(items, old_positions))

    def on_items_moved_by_mouse(self, items):
         self.undo_stack.push(MoveByMouseCommand(items))

    def on_items_moved_by_key(self, items):
        self.undo_stack.push(MoveByKeyCommand(items))

    def undo(self):
        self.undo_stack.undo()

    def redo(self):
        self.undo_stack.redo()

    # @Slot()
    # def process_undo(self):
    #     pass
    #
    # @Slot()
    # def process_redo(self):
    #     pass

    # @Slot(list, list)
    # def on_item_moved(self, moved_items, old_positions):
    #     pass

    # def isAnySelected(self):
    #     return len(self.diagramScene.selectedItems()) != 0
    #
    # @Slot(DiagramItem, QPointF)
    # def onItemMoved(self, movedItem, oldPosition):
    #     self.undoStack.push(MoveCommand(movedItem, oldPosition))
    #
    # @Slot()
    # def deleteItem(self):
    #     if not self.isAnySelected():
    #         return
    #
    #     deleteCommand = DeleteCommand(self.diagramScene)
    #     self.undoStack.push(deleteCommand)
    #
    # @Slot()
    # def itemMenuAboutToHide(self):
    #     self.deleteAction.setEnabled(True)
    #
    # @Slot()
    # def itemMenuAboutToShow(self):
    #     self.deleteAction.setEnabled(self.isAnySelected())
    #
    # @Slot()
    # def addBox(self):
    #     addCommand = AddCommand(DiagramItemType.Box,
    #                             self.diagramScene)
    #     self.undoStack.push(addCommand)
    #
    # @Slot()
    # def addTriangle(self):
    #     addCommand = AddCommand(DiagramItemType.Triangle,
    #                             self.diagramScene)
    #     self.undoStack.push(addCommand)

