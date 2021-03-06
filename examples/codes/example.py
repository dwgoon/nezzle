from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import EdgeClassFactory
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import Network


def update(nav, net):
    """Update the navigation by creating or modifying network graphics.
       This function is called by Nezzle, when pushing the "run" button.

    Args:
        nav: the navigation widget that manages network items.
        net: the currently selected network item in the networks.
    """


    new_net = Network('Two edges')

    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
    EdgeClass = EdgeClassFactory.create("STRAIGHT_EDGE")
    TriangleClass = ArrowClassFactory.create("TRIANGLE")
    HammerClass = ArrowClassFactory.create("HAMMER")
    LabelClass = LabelClassFactory.create("TEXT_LABEL")

    x0 = -70.0
    y0 = 0.0

    x1 = 70.0
    y1 = 0.0

    src = NodeClass('SRC1', 40, 40, pos=QPointF(x0, y0))
    src["FILL_COLOR"] = QColor(51, 102, 255)
    src["BORDER_COLOR"] = Qt.black
    src["BORDER_WIDTH"] = 2
    new_net.add_node(src)

    label = LabelClass(src, "A")
    label["FONT_SIZE"] = 20
    label["TEXT_COLOR"] = QColor(255, 255, 255)
    label.align()
    new_net.add_label(label)

    trg = NodeClass('TGT1', 40, 40, pos=QPointF(x1, y1))
    trg["FILL_COLOR"] = QColor(255, 153, 51)
    trg["BORDER_COLOR"] = Qt.black
    trg["BORDER_WIDTH"] = 2
    new_net.add_node(trg)

    label = LabelClass(trg, "B")
    label["FONT_SIZE"] = 20
    label.align()
    new_net.add_label(label)

    head = TriangleClass(width=10, height=10, offset=4)
    edge = EdgeClass("EDGE1", src, trg, width=4, head=head)
    edge["FILL_COLOR"] = Qt.black
    new_net.add_edge(edge)


    x0 = -70.0
    y0 = 50.0

    x1 = 70.0
    y1 = 50.0

    src = NodeClass('SRC2', 40, 40, pos=QPointF(x0, y0))
    src["FILL_COLOR"] = QColor(51, 102, 255)
    src["BORDER_COLOR"] = Qt.black
    src["BORDER_WIDTH"] = 2
    new_net.add_node(src)

    label = LabelClass(src, "C")
    label["FONT_SIZE"] = 20
    label["TEXT_COLOR"] = QColor(255, 255, 255)
    label.align()
    new_net.add_label(label)

    trg = NodeClass('TGT2', 40, 40, pos=QPointF(x1, y1))
    trg["FILL_COLOR"] = QColor(255, 153, 51)
    trg["BORDER_COLOR"] = Qt.black
    trg["BORDER_WIDTH"] = 2
    new_net.add_node(trg)

    label = LabelClass(trg, "D")
    label["FONT_SIZE"] = 20
    label.align()
    new_net.add_label(label)

    head = HammerClass(width=14, height=4, offset=4)
    edge = EdgeClass("EDGE2", src, trg, width=4, head=head)
    edge["FILL_COLOR"] = Qt.black
    new_net.add_edge(edge)

    nav.append_item(new_net)