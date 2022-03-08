from nezzle.graphics.edges.straightedge import StraightEdge
from nezzle.graphics.edges.curvededge import CurvedEdge
from nezzle.graphics.edges.elbowedge import VerticalElbowEdge
from nezzle.graphics.edges.elbowedge import HorizontalElbowEdge
from nezzle.graphics.edges.selfloopedge import SelfloopEdge


class EdgeClassFactory(object):

    @staticmethod
    def create(edge_type):
        if edge_type.upper() == 'STRAIGHT_EDGE':
            return StraightEdge
        elif edge_type.upper() == "VERTICAL_ELBOW_EDGE":
            return VerticalElbowEdge
        elif edge_type.upper() == "HORIZONTAL_ELBOW_EDGE":
            return HorizontalElbowEdge
        elif edge_type.upper() == 'CURVED_EDGE':
            return CurvedEdge
        elif edge_type.upper() == 'SELFLOOP_EDGE':
            return SelfloopEdge
        else:
            raise TypeError("Undefined edge type: %s" % (edge_type))
