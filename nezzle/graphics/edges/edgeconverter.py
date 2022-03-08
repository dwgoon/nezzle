from typing import AnyStr
from typing import Union
from typing import Type

from nezzle.graphics.edges.baseedge import BaseEdge
from nezzle.graphics.edges.edgefactory import EdgeClassFactory


class EdgeConverter(object):

    @staticmethod
    def convert(edge: BaseEdge, edge_type: Union[Type, AnyStr]):

        if isinstance(edge_type, str):
            edge_type = EdgeClassFactory.create(edge_type)

        if type(edge) == edge_type:
            return

        attr = edge.to_dict()
        attr["ITEM_TYPE"] = edge_type.ITEM_TYPE
        new_edge = edge_type.from_dict(attr=attr, source=edge.source, target=edge.target)
        return new_edge
