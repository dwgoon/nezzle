from datetime import datetime

from qtpy.QtCore import QPointF
from qtpy.QtWidgets import QUndoCommand

from nezzle.graphics.nodes.basenode import BaseNode
from nezzle.graphics.links.controlpoint import ControlPoint
from nezzle.graphics.links.controlpoint import ConnectorControlPoint
from nezzle.graphics.links.linkfactory import LinkClassFactory
from nezzle.graphics.nodes.nodefactory import NodeClassFactory


class MoveByMouseCommand(QUndoCommand):
    ID = 0

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self._items = items
        self._new_positions = []
        self._old_positions = []

        for item in items:
            self._new_positions.append((item, QPointF(item.pos())))
            self._old_positions.append((item, QPointF(item["_OLD_POS"])))

            children = item.childItems()
            if not children:
                children = []

            if isinstance(item, BaseNode):
                for link in item.links:
                    for child in link.childItems():
                        if child not in children:
                            children.append(child)

            if children:
                for child in children:
                    self._new_positions.append((child, QPointF(child.pos())))
                    self._old_positions.append((child, QPointF(child["_OLD_POS"])))

        # end of for
        print("[OLD_POS]", self._old_positions)
        print("[NEW_POS]", self._new_positions)

    def id(self):
        return self.ID

    def undo(self):
        item = self._items[0]
        scene = item.scene()
        selected = scene.selectedItems()
        scene.clearSelection()
        scene.clearFocus()

        print("[MoveByMouseCommand UNDO]")
        for i, (item, pos) in enumerate(self._old_positions):

            if isinstance(item, ConnectorControlPoint):
                item.setSelected(True)
                item.setPos(pos)
                item.parent.update()
                item.setSelected(False)
            else:
                item.setPos(pos)

            new_item, new_pos = self._new_positions[i]
            print(item, pos, new_item, new_pos)

        for selected_item in selected:
            selected_item.setSelected(True)

        scene.update()
        # now = datetime.now()  # current date and time
        # str_now = now.strftime("[UNDO %Y-%m-%d %H:%M:%S]")
        # self.setText(str_now + " " + self._text)
        self.setText(self._text)


    def redo(self):
        print("[MoveByMouseCommand REDO]")
        for i, (item, pos) in enumerate(self._new_positions):
            if isinstance(item, ConnectorControlPoint):
                item.setSelected(True)
                item.setPos(pos)
                item.parent.update()
                item.setSelected(False)
            else:
                item.setPos(pos)

            old_item, old_pos = self._old_positions[i]
            print(item, pos, old_item, old_pos)

        item.scene().update()

        num_items = len(self._items)
        if num_items == 1:
            item = self._items[0]
            _, old_pos = self._old_positions[0]
            self._text = f"Move {str(item)} from ({old_pos.x():.2f}, {old_pos.y():.2f}) to ({item.x():.2f}, {item.y():.2f})"
        else:
            if isinstance(self._items[0], ControlPoint):
                self._text = f"Move {num_items} control points"
            else:
                self._text = f"Move {num_items} Items"

        #now = datetime.now()  # current date and time
        #str_now = now.strftime("[REDO %Y-%m-%d %H:%M:%S]")
        #self.setText(str_now + " " + self._text)
        self.setText(self._text)

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

        if not isinstance(command, MoveByKeyCommand):
            return False

        # self._new_positions = {item.iden:QPointF(item.pos()) for item in items}
        items = command._items
        self._new_positions = [(item, QPointF(item.pos())) for item in items]

        num_items = len(self._items)
        if num_items == 1:
            item = self._items[0]
            old_pos = item.pos()
            _, new_pos = self._new_positions[0]
            self._text = f"Move {str(item)} from ({old_pos.x():.2f}, {old_pos.y():.2f}) to ({new_pos.x():.2f}, {new_pos.y():.2f})"
        else:
            self._text = f"Move {num_items} Items"
        self.setText(self._text)
        return True


class ConvertNodeCommand(QUndoCommand):
    ID = 2

    def __init__(self, net, old_items, new_items, parent=None):
        super().__init__(parent)
        self._net = net
        self._old_items = old_items
        self._new_items = new_items

    def undo(self):
        print("[ConvertNodeCommand UNDO]")
        for old_item, new_item in zip(self._old_items, self._new_items):
            old_item.setSelected(new_item.isSelected())
            self._net.replace_node(new_item, old_item)
            old_item.update_children_old_positions()
            old_item["_OLD_POS"] = old_item.pos()
            print(new_item, old_item)

        old_item.scene().update()
        self.setText(self._text)

    def redo(self):
        print("[ConvertNodeCommand REDO]")
        for old_item, new_item in zip(self._old_items, self._new_items):
            new_item.setSelected(old_item.isSelected())
            self._net.replace_node(old_item, new_item)
            new_item.update_children_old_positions()
            new_item["_OLD_POS"] = new_item.pos()
            print(old_item, new_item)

        new_item.scene().update()

        NewNodeClass = NodeClassFactory.create(new_item.ITEM_TYPE)
        num_items = len(self._old_items)
        if num_items == 1:
            old_item = self._old_items[0]
            new_item = self._new_items[0]

            self._text = f"Convert {str(old_item)} to {NewNodeClass.__name__}"
        else:
            self._text = f"Convert {num_items} items to {NewNodeClass.__name__}"

        self.setText(self._text)


class ConvertLinkCommand(QUndoCommand):
    ID = 3

    def id(self):
        return self.ID

    def __init__(self, net, old_items, new_items, parent=None):
        super().__init__(parent)
        self._net = net
        self._old_items = old_items  # [item.copy() for item in new_items]
        self._new_items = new_items  # [item.copy() for item in old_items]

    def undo(self):
        print("[ConvertLinkCommand UNDO]")
        for old_item, new_item in zip(self._old_items, self._new_items):
            old_item.setSelected(new_item.isSelected())
            self._net.replace_link(new_item, old_item)
            old_item.update_children_old_positions()
            old_item["_OLD_POS"] = new_item.pos()
            print(new_item, old_item)

        old_item.scene().update()
        self.setText(self._text)

    def redo(self):
        print("[ConvertLinkCommand REDO]")
        for old_item, new_item in zip(self._old_items, self._new_items):
            new_item.setSelected(old_item.isSelected())
            self._net.replace_link(old_item, new_item)
            new_item.update_children_old_positions()
            new_item["_OLD_POS"] = new_item.pos()
            print(old_item, new_item)

        new_item.scene().update()

        NewLinkClass = LinkClassFactory.create(new_item.ITEM_TYPE)
        num_items = len(self._old_items)
        if num_items == 1:
            old_item = self._old_items[0]
            new_item = self._new_items[0]
            self._text = f"Convert {str(old_item)} to {NewLinkClass.__name__}"
        else:
            self._text = f"Convert {num_items} Items to {NewLinkClass.__name__}"

        self.setText(self._text)

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

