from datetime import datetime

from qtpy.QtCore import QPointF
from qtpy.QtWidgets import QUndoCommand

from nezzle.graphics.nodes.basenode import BaseNode
from nezzle.graphics.edges.controlpoint import ControlPoint
from nezzle.graphics.edges.controlpoint import ConnectorControlPoint
from nezzle.graphics.edges.edgefactory import EdgeClassFactory
from nezzle.graphics.nodes.nodefactory import NodeClassFactory


class MoveByMouseCommand(QUndoCommand):
    ID = 0

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self._items = items
        self._new_positions = []
        self._old_positions = []
        self._text = ""

        for item in items:
            self._new_positions.append((item, QPointF(item.pos())))
            self._old_positions.append((item, QPointF(item["_OLD_POS"])))

            children = list(item.childItems())

            if isinstance(item, BaseNode):
                # Disjoint by construction: each child has exactly one
                # parent and add_edge deduplicates edges, so no membership
                # scan is needed.
                for edge in item.edges:
                    children.extend(edge.childItems())

            for child in children:
                new_pos = QPointF(child.pos())
                old_pos = QPointF(child["_OLD_POS"])
                if new_pos == old_pos:
                    # setPos to an identical position is a Qt no-op, so
                    # recording unchanged children only bloats the command
                    # (e.g. control points during a plain node drag).
                    continue
                self._new_positions.append((child, new_pos))
                self._old_positions.append((child, old_pos))

        # end of for

    def id(self):
        return self.ID

    def undo(self):
        item = self._items[0]
        scene = item.scene()
        selected = scene.selectedItems()
        scene.clearSelection()
        scene.clearFocus()

        for i, (item, pos) in enumerate(self._old_positions):

            if isinstance(item, ConnectorControlPoint):
                item.setSelected(True)
                item.setPos(pos)
                item.parent.update()
                item.setSelected(False)
            else:
                item.setPos(pos)

        for selected_item in selected:
            selected_item.setSelected(True)

        self.setText(self._text)

    def redo(self):
        for i, (item, pos) in enumerate(self._new_positions):
            if isinstance(item, ConnectorControlPoint):
                old_selected = item.isSelected()
                item.setSelected(True)
                item.setPos(pos)
                item.parent.update()
                item.setSelected(old_selected)
            else:
                item.setPos(pos)

        # end of for
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

        if [it for it, _ in self._old_positions] != [it for it, _ in command._old_positions]:
            return False

        self._new_positions = list(command._new_positions)

        num_items = len(self._items)
        if num_items == 1:
            item = self._items[0]
            _, old_pos = self._old_positions[0]
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
        self._text = ""

    def undo(self):
        for old_item, new_item in zip(self._old_items, self._new_items):
            old_item.setSelected(new_item.isSelected())
            self._net.replace_node(new_item, old_item)
            old_item.update_children_old_positions()
            old_item["_OLD_POS"] = old_item.pos()

        self.setText(self._text)

    def redo(self):
        for old_item, new_item in zip(self._old_items, self._new_items):
            new_item.setSelected(old_item.isSelected())
            self._net.replace_node(old_item, new_item)
            new_item.update_children_old_positions()
            new_item["_OLD_POS"] = new_item.pos()

        NewNodeClass = NodeClassFactory.create(new_item.ITEM_TYPE)
        num_items = len(self._old_items)
        if num_items == 1:
            old_item = self._old_items[0]
            new_item = self._new_items[0]

            self._text = f"Convert {str(old_item)} to {NewNodeClass.__name__}"
        else:
            self._text = f"Convert {num_items} items to {NewNodeClass.__name__}"

        self.setText(self._text)


class ConvertEdgeCommand(QUndoCommand):
    ID = 3

    def id(self):
        return self.ID

    def __init__(self, net, old_items, new_items, parent=None):
        super().__init__(parent)
        self._net = net
        self._old_items = old_items  # [item.copy() for item in new_items]
        self._new_items = new_items  # [item.copy() for item in old_items]
        self._text = ""

    def undo(self):
        for old_item, new_item in zip(self._old_items, self._new_items):
            old_item.setSelected(new_item.isSelected())
            self._net.replace_edge(new_item, old_item)
            old_item.update_children_old_positions()
            old_item["_OLD_POS"] = old_item.pos()

        self.setText(self._text)

    def redo(self):
        for old_item, new_item in zip(self._old_items, self._new_items):
            new_item.setSelected(old_item.isSelected())
            self._net.replace_edge(old_item, new_item)
            new_item.update_children_old_positions()
            new_item["_OLD_POS"] = new_item.pos()

        NewEdgeClass = EdgeClassFactory.create(new_item.ITEM_TYPE)
        num_items = len(self._old_items)
        if num_items == 1:
            old_item = self._old_items[0]
            new_item = self._new_items[0]
            self._text = f"Convert {str(old_item)} to {NewEdgeClass.__name__}"
        else:
            self._text = f"Convert {num_items} Items to {NewEdgeClass.__name__}"

        self.setText(self._text)
