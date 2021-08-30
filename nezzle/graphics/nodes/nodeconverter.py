from typing import AnyStr
from typing import Union
from typing import Type

from nezzle.graphics.nodes.basenode import BaseNode
from nezzle.graphics.nodes.nodefactory import NodeClassFactory


class NodeConverter(object):

    @staticmethod
    def convert(node: BaseNode, node_type: Union[Type, AnyStr]):
        if isinstance(node_type, str):
            node_type = NodeClassFactory.create(node_type)

        if type(node) == node_type:
            return

        attr = node.to_dict()
        new_node = node_type.from_dict(attr=attr)
        return new_node
