"""
Create 2-node negative feedback loop (2NNFL)
"""

from qtpy.QtCore import QPoint, Qt

from nezzle.graphics import HeaderClassFactory
from nezzle.graphics import LinkClassFactory
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
    LinkClass = LinkClassFactory.create("CURVED_LINK")
    ArrowClass = HeaderClassFactory.create('ARROW')
    HammerClass = HeaderClassFactory.create('HAMMER')

    # Create two nodes
    src = NodeClass('SRC', 40, 40, pos=QPoint(x0, y0))
    src['FILL_COLOR'] = Qt.yellow
    src["BORDER_COLOR"] = Qt.black
    src['BORDER_WIDTH'] = 2

    tgt = NodeClass('TGT', 40, 40, pos=QPoint(x1, y1))
    tgt['FILL_COLOR'] = Qt.yellow
    tgt["BORDER_COLOR"] = Qt.black
    tgt['BORDER_WIDTH'] = 2

    new_net.add_node(src)
    new_net.add_node(tgt)

    # Create two links
    header = ArrowClass(width=10, height=10, offset=4)
    link1 = LinkClass("LINK1", src, tgt, width=4, header=header)
    link1["FILL_COLOR"] = Qt.black
    link1["CTRL_POS_X"] = -10
    link1["CTRL_POS_Y"] = -50

    header = HammerClass(width=16, height=3, offset=4)
    link2 = LinkClass("LINK2", tgt, src, width=4, header=header)
    link2["FILL_COLOR"] = Qt.black
    link2["CTRL_POS_X"] = 10
    link2["CTRL_POS_Y"] = 50

    new_net.add_link(link1)
    new_net.add_link(link2)

    # Create labels
    LabelClass = LabelClassFactory.create("TEXT_LABEL")
    for (node, name) in [(src, "A"), (tgt, "B")]:
        label = LabelClass(node, name)
        label["FONT_SIZE"] = 20
        label.align()
        new_net.add_label(label)

    # Append new network to navigation panel
    nav.append_item(new_net)
