"""
Create 3-node negative feedback loop (3NNFL)
"""

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF

from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import EdgeClassFactory
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import Network


def update(nav, net):
    new_net = Network('3NNFL')

    x0 = -144.5
    y0 = -9.85

    x1 = -73.125
    y1 = -56.5

    x2 = -15.33
    y2 = 41.24

    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
    EdgeClass = EdgeClassFactory.create("VERTICAL_ELBOW_EDGE")
    ArrowClass = ArrowClassFactory.create("TRIANGLE")
    HammerClass = ArrowClassFactory.create("HAMMER")

    # Create two nodes
    node1 = NodeClass('NODE1', 40, 40, pos=QPointF(x0, y0))
    node1["FILL_COLOR"] = Qt.yellow
    node1["BORDER_COLOR"] = Qt.black
    node1["BORDER_WIDTH"] = 2

    node2 = NodeClass('NODE2', 40, 40, pos=QPointF(x1, y1))
    node2["FILL_COLOR"] = Qt.yellow
    node2["BORDER_COLOR"] = Qt.black
    node2["BORDER_WIDTH"] = 2

    node3 = NodeClass('NODE3', 40, 40, pos=QPointF(x2, y2))
    node3["FILL_COLOR"] = Qt.yellow
    node3["BORDER_COLOR"] = Qt.black
    node3["BORDER_WIDTH"] = 2

    new_net.add_node(node1)
    new_net.add_node(node2)
    new_net.add_node(node3)

    # Create two edges
    head = ArrowClass(width=10, height=10, offset=4)
    edge1 = EdgeClass("EDGE1", node1, node2, width=4, head=head)
    edge1["FILL_COLOR"] = Qt.black
    edge1["CP_POS_X"] = -10
    edge1["CP_POS_Y"] = -50

    head = ArrowClass(width=10, height=10, offset=4)
    edge2 = EdgeClass("EDGE2", node2, node3, width=4, head=head)
    edge2["FILL_COLOR"] = Qt.black
    edge2["CP_POS_X"] = -10
    edge2["CP_POS_Y"] = -50

    head = HammerClass(width=16, height=3, offset=4)
    edge3 = EdgeClass("EDGE3", node3, node1, width=4, head=head)
    edge3["FILL_COLOR"] = Qt.black
    edge3["CP_POS_X"] = 10
    edge3["CP_POS_Y"] = 50

    new_net.add_edge(edge1)
    new_net.add_edge(edge2)
    new_net.add_edge(edge3)

    # Create labels
    LabelClass = LabelClassFactory.create("TEXT_LABEL")
    for (node, name) in [(node1, "A"), (node2, "B"), (node3, "C")]:
        label = LabelClass(node, name)
        label["FONT_SIZE"] = 20
        label.align()
        new_net.add_label(label)

    # Append the new network to the network tree view.
    nav.append_item(new_net)
