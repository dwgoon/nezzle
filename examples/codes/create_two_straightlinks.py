"""
Create two straight links
"""

from qtpy.QtCore import Qt
from qtpy.QtCore import QPoint
from qtpy.QtGui import QColor

from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import LinkClassFactory
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import Network


def update(nav, net):
    new_net = Network('2NNFL')

    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
    LinkClass = LinkClassFactory.create("STRAIGHT_LINK")
    ArrowClass = ArrowClassFactory.create('TRIANGLE')
    HammerClass = ArrowClassFactory.create('HAMMER')

    # Create four nodes
    x0 = -70.0
    y0 = 0.0

    x1 = 70.0
    y1 = 0.0

    src1 = NodeClass('SRC1', 40, 40, pos=QPoint(x0, y0))
    src1['FILL_COLOR'] = Qt.yellow
    src1["BORDER_COLOR"] = Qt.black
    src1['BORDER_WIDTH'] = 2

    tgt1 = NodeClass('TGT1', 40, 40, pos=QPoint(x1, y1))
    tgt1['FILL_COLOR'] = Qt.yellow
    tgt1["BORDER_COLOR"] = Qt.black
    tgt1['BORDER_WIDTH'] = 2


    x0 = -70.0
    y0 = 100.0

    x1 = 70.0
    y1 = 100.0

    src2 = NodeClass('SRC2', 40, 40, pos=QPoint(x0, y0))
    src2['FILL_COLOR'] = QColor(255, 165, 0)
    src2["BORDER_COLOR"] = Qt.black
    src2['BORDER_WIDTH'] = 2

    tgt2 = NodeClass('TGT2', 40, 40, pos=QPoint(x1, y1))
    tgt2['FILL_COLOR'] = QColor(255, 165, 0)
    tgt2["BORDER_COLOR"] = Qt.black
    tgt2['BORDER_WIDTH'] = 2

    new_net.add_node(src1)
    new_net.add_node(tgt1)
    new_net.add_node(src2)
    new_net.add_node(tgt2)

    # Create two links
    head = ArrowClass(width=10, height=10, offset=4)
    link1 = LinkClass("LINK1", src1, tgt1, width=4, head=head)
    link1["FILL_COLOR"] = Qt.black
    link1["CTRL_POS_X"] = -10
    link1["CTRL_POS_Y"] = -50

    head = HammerClass(width=16, height=3, offset=4)
    link2 = LinkClass("LINK2", src2, tgt2, width=4, head=head)
    link2["FILL_COLOR"] = Qt.black
    link2["CTRL_POS_X"] = 10
    link2["CTRL_POS_Y"] = 50

    new_net.add_link(link1)
    new_net.add_link(link2)

    # Create labels
    LabelClass = LabelClassFactory.create("TEXT_LABEL")
    for (node, name) in [(src1, "A"), (tgt1, "B"), (src2, "C"), (tgt2, "D")]:
        label = LabelClass(node, name)
        label["FONT_SIZE"] = 20
        label.align()
        new_net.add_label(label)

    # Append new network to navigation panel
    nav.append_item(new_net)