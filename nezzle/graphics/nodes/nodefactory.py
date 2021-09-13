from nezzle.graphics.nodes.ellipsenode import EllipseNode
from nezzle.graphics.nodes.ellipsenode import CircleNode
from nezzle.graphics.nodes.rectanglenode import RectangleNode
from nezzle.graphics.nodes.rectanglenode import SquareNode


class NodeClassFactory(object):
    @staticmethod
    def create(node_type):
        if node_type.upper() == "ELLIPSE_NODE":
            return EllipseNode
        elif node_type.upper() == "CIRCLE_NODE":
            return CircleNode
        elif node_type.upper() == "RECTANGLE_NODE":
            return RectangleNode
        elif node_type.upper() == "SQUARE_NODE":
            return SquareNode
        else:
            raise TypeError("Undefined nodes type: %s" % (node_type))
