import math

from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import CurvedEdge
from nezzle.graphics import Triangle, Hammer
from nezzle.graphics import Network


def update(nav, net):
    net = Network('complete-100n')

    num_nodes = 100
    radius_layout = 900  # Circular layout radius

    for i in range(num_nodes):
        angle = 2 * math.pi * i / num_nodes
        x = radius_layout * math.cos(angle)
        y = radius_layout * math.sin(angle)

        node = EllipseNode(str(i), 40, 40, pos=QPointF(x, y))
        node["FILL_COLOR"] = "white"
        node["BORDER_COLOR"] = "black"
        node["BORDER_WIDTH"] = 2

        label = TextLabel(node, node.iden)
        label["FONT_SIZE"] = 20
        label.align()

        net.add_node(node)
        net.add_label(label)
    # end of for

    # Complete graph: one edge per unordered node pair (n*(n-1)/2 = 4950)
    for i in range(num_nodes):
        src = net.nodes[str(i)]
        for j in range(i + 1, num_nodes):
            trg = net.nodes[str(j)]

            if (i + j) % 2 == 0:
                head = Triangle(width=8, height=8, offset=3)
                edge = CurvedEdge("EDGE(%s+%s)"%(src.iden, trg.iden),
                                  src, trg, width=2, head=head)
            else:
                head = Hammer(width=12, height=3, offset=3)
                edge = CurvedEdge("EDGE(%s-%s)"%(src.iden, trg.iden),
                                  src, trg, width=2, head=head)

            edge["FILL_COLOR"] = QColor(0, 0, 0, 60)

            net.add_edge(edge)
        # end of for
    # end of for

    nav.append_item(net)
