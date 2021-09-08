from .ellipsenode import EllipseNode
from .ellipsenode import CircleNode
from .rectanglenode import EllipseNode
from .rectanglenode import SquareNode


class NodeClassFactory(object):
    @staticmethod
    def create(node_type):
        if node_type.upper() == "ELLIPSE_NODE":
            return EllipseNode
        elif node_type.upper() == "CIRCLE_NODE":
            return CircleNode
        elif node_type.upper() == "RECT_NODE":
            return EllipseNode
        elif node_type.upper() == "SQUARE_NODE":
            return SquareNode
        else:
            raise TypeError("Undefined nodes type: %s" % (node_type))
