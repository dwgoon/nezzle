import numpy as np

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF

from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import CurvedEdge
from nezzle.graphics import Triangle, Hammer
from nezzle.graphics import Network


def update(nav, net):
    net = Network('100-network')

    num_nodes = 100
    num_edges = 400
    positions = np.random.uniform(-1000, 1000, size=(num_nodes, 2))

    for i, pos in enumerate(positions):
        node = EllipseNode(str(i), 40, 40, pos=QPointF(pos[0], pos[1]))
        node["FILL_COLOR"] = Qt.white
        node["BORDER_COLOR"] = Qt.black
        node["BORDER_WIDTH"] = 2

        label = TextLabel(node, node.iden)
        label["FONT_SIZE"] = 20
        label.align()

        net.add_node(node)
        net.add_label(label)
    # end of for

    connections = np.random.randint(0, num_nodes, size=(num_edges, 2))
    for i, conn in enumerate(connections):
        src = net.nodes[str(conn[0])]
        trg = net.nodes[str(conn[1])]

        if np.random.randn() < 0.5:
            head = Triangle(width=10, height=10, offset=4)
            edge = CurvedEdge("EDGE%d(%s+%s)"%(i, src.iden, trg.iden), src, trg, width=4, head=head)

        else:
            head = Hammer(width=16, height=3, offset=4)
            edge = CurvedEdge("EDGE%d(%s-%s)"%(i, src.iden, trg.iden), src, trg, width=4, head=head)

        edge["FILL_COLOR"] = Qt.black
        edge["CP_POS_X"] = -10
        edge["CP_POS_Y"] = -50

        net.add_edge(edge)


    nav.append_item(net)