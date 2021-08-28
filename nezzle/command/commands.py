from qtpy.QtCore import QPointF
from qtpy.QtWidgets import QUndoCommand


class MoveByMouseCommand(QUndoCommand):
    ID = 0

    def id(self):
        return self.ID

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self._items = items
        self._new_positions = {item.iden:QPointF(item.pos()) for item in items}
        self._old_positions = {item.iden:QPointF(item["_OLD_POS"]) for item in items}

    def undo(self):
        for i, item in enumerate(self._items):
            item.setPos(self._old_positions[item.iden])

        item.scene().update()
        self.setText("Moving to new positions")

    def redo(self):
        for i, item in enumerate(self._items):
            item.setPos(self._new_positions[item.iden])

        item.scene().update()
        self.setText("Moving to new positions")


class MoveByKeyCommand(MoveByMouseCommand):
    ID = 1

    def id(self):
        return self.ID
    """
    The mergeWith() makes the consecutive moves a single MoveCommand,
    (i.e., the item will be moved back to the first position,
          when undo is performed.)
    """
    def mergeWith(self, command):
        items = command._items

        if not isinstance(command, MoveByKeyCommand):
            return False

        self._new_positions = {item.iden:QPointF(item.pos()) for item in items}
        self.setText("Moving to new positions")
        return True


# class DeleteCommand(QUndoCommand):
#
#     def __init__(self, scene, parent=None):
#         super().__init__(parent)
#
#         self.myGraphicsScene = scene
#         items = self.myGraphicsScene.selectedItems()
#         items[0].setSelected(False)
#         self.myDiagramItem = items[0]
#         fstr = "Delete %s" % create_command_str(self.myDiagramItem,
#                                                 self.myDiagramItem.pos())
#         self.setText(fstr)
#
#     def undo(self):
#         self.myGraphicsScene.addItem(self.myDiagramItem)
#         self.myGraphicsScene.update()
#
#     def redo(self):
#         self.myGraphicsScene.removeItem(self.myDiagramItem)
#
#
# class AddCommand(QUndoCommand):
#
#     def __init__(self, addType, scene, parent=None):
#         super().__init__(parent)
#
#         self.myGraphicsScene = scene
#         self.myDiagramItem = DiagramItem(addType)
#         self.initialPosition = QPointF((qrand() % 10) + int(scene.width() / 2),
#                                        (qrand() % 10) + int(scene.height() / 2))
#         scene.update()
#
#         fstr = "Add %s" % (create_command_str(self.myDiagramItem,
#                                               self.initialPosition))
#         self.setText(fstr)
#
#     def __del__(self):
#         if not self.myDiagramItem.scene():
#             del self.myDiagramItem
#
#     def undo(self):
#         self.myGraphicsScene.removeItem(self.myDiagramItem)
#         self.myGraphicsScene.update()
#
#     def redo(self):
#         self.myGraphicsScene.addItem(self.myDiagramItem)
#         self.myDiagramItem.setPos(self.initialPosition)
#         self.myGraphicsScene.clearSelection()
#         self.myGraphicsScene.update()

