from typing import ClassVar

from nezzle.graphics.nodes.basenode import BaseNode

class NodeConverter(object):

    @staticmethod
    def to_node(node: BaseNode, node_type: ClassVar):

        if type(node) == node_type:
            return

        attr = node.to_dict()
        new_node = node_type.from_dict(attr=attr)
        return new_node
