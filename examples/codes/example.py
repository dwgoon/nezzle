from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import LinkClassFactory
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import Network


def update(nav, net):
    new_net = Network('Two links')

    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
    LinkClass = LinkClassFactory.create("STRAIGHT_LINK")
    TriangleClass = ArrowClassFactory.create('TRIANGLE')
    HammerClass = ArrowClassFactory.create('HAMMER')
    LabelClass = LabelClassFactory.create("TEXT_LABEL")

    x0 = -70.0
    y0 = 0.0

    x1 = 70.0
    y1 = 0.0

    src = NodeClass('SRC1', 40, 40, pos=QPointF(x0, y0))
    src['FILL_COLOR'] = QColor(51, 102, 255)
    src["BORDER_COLOR"] = Qt.black
    src['BORDER_WIDTH'] = 2
    new_net.add_node(src)

    label = LabelClass(src, "A")
    label["FONT_SIZE"] = 20
    label["TEXT_COLOR"] = QColor(255, 255, 255)
    label.align()
    new_net.add_label(label)

    tgt = NodeClass('TGT1', 40, 40, pos=QPointF(x1, y1))
    tgt['FILL_COLOR'] = QColor(255, 153, 51)
    tgt["BORDER_COLOR"] = Qt.black
    tgt['BORDER_WIDTH'] = 2
    new_net.add_node(tgt)

    label = LabelClass(tgt, "B")
    label["FONT_SIZE"] = 20
    label.align()
    new_net.add_label(label)

    head = TriangleClass(width=10, height=10, offset=4)
    link = LinkClass("LINK1", src, tgt, width=4, head=head)
    link["FILL_COLOR"] = Qt.black
    new_net.add_link(link)


    x0 = -70.0
    y0 = 50.0

    x1 = 70.0
    y1 = 50.0

    src = NodeClass('SRC2', 40, 40, pos=QPointF(x0, y0))
    src['FILL_COLOR'] = QColor(51, 102, 255)
    src["BORDER_COLOR"] = Qt.black
    src['BORDER_WIDTH'] = 2
    new_net.add_node(src)

    label = LabelClass(src, "C")
    label["FONT_SIZE"] = 20
    label["TEXT_COLOR"] = QColor(255, 255, 255)
    label.align()
    new_net.add_label(label)

    tgt = NodeClass('TGT2', 40, 40, pos=QPointF(x1, y1))
    tgt['FILL_COLOR'] = QColor(255, 153, 51)
    tgt["BORDER_COLOR"] = Qt.black
    tgt['BORDER_WIDTH'] = 2
    new_net.add_node(tgt)

    label = LabelClass(tgt, "D")
    label["FONT_SIZE"] = 20
    label.align()
    new_net.add_label(label)

    head = HammerClass(width=14, height=4, offset=4)
    link = LinkClass("LINK2", src, tgt, width=4, head=head)
    link["FILL_COLOR"] = Qt.black
    new_net.add_link(link)

    nav.append_item(new_net)