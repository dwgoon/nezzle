"""
Create 2-node negative feedback loop (2NNFL)
"""

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF

from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import EdgeClassFactory
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import Network


def update(nav, net):
    new_net = Network('2NNFL')

    x0 = -70.0
    y0 = 0.0

    x1 = 70.0
    y1 = 0.0

    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
    EdgeClass = EdgeClassFactory.create("CURVED_EDGE")
    ArrowClass = ArrowClassFactory.create("TRIANGLE")
    HammerClass = ArrowClassFactory.create("HAMMER")

    # Create two nodes
    src = NodeClass('SRC', 40, 40, pos=QPointF(x0, y0))
    src["FILL_COLOR"] = Qt.yellow
    src["BORDER_COLOR"] = Qt.black
    src["BORDER_WIDTH"] = 2

    tgt = NodeClass('TGT', 40, 40, pos=QPointF(x1, y1))
    tgt["FILL_COLOR"] = Qt.yellow
    tgt["BORDER_COLOR"] = Qt.black
    tgt["BORDER_WIDTH"] = 2

    new_net.add_node(src)
    new_net.add_node(tgt)

    # Create two edges
    head = ArrowClass(width=10, height=10, offset=4)
    edge1 = EdgeClass("EDGE1", src, tgt, width=4, head=head)
    edge1["FILL_COLOR"] = Qt.black
    edge1["CP_POS_X"] = -10
    edge1["CP_POS_Y"] = -50

    head = HammerClass(width=16, height=3, offset=4)
    edge2 = EdgeClass("EDGE2", tgt, src, width=4, head=head)
    edge2["FILL_COLOR"] = Qt.black
    edge2["CP_POS_X"] = 10
    edge2["CP_POS_Y"] = 50

    new_net.add_edge(edge1)
    new_net.add_edge(edge2)

    # Create labels
    LabelClass = LabelClassFactory.create("TEXT_LABEL")
    for (node, name) in [(src, "A"), (tgt, "B")]:
        label = LabelClass(node, name)
        label["FONT_SIZE"] = 20
        label.align()
        new_net.add_label(label)

    # Append new network to navigation panel
    nav.append_item(new_net)
