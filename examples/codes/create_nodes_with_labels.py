from qtpy.QtCore import QPoint, Qt
from qtpy.QtGui import QColor

from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import LinkClassFactory
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import Network


def update(nav, net):
    _net = Network('TestNetwork')

    x0 = 400.0
    y0 = 200.0

    x1 = 600.0
    y1 = 200.0

    # A single arrow link with circle nodes
    NodeClass = NodeClassFactory.create("RECTANGLE_NODE")

    src = NodeClass('source', 80, 40, pos=QPoint(x1, y1))
    tgt = NodeClass('target', 80, 40, pos=QPoint(x0, y0))

    src["FILL_COLOR"] = Qt.cyan
    tgt["FILL_COLOR"] = Qt.cyan

    LinkClass = LinkClassFactory.create("CURVED_LINK")

    ArrowClass = ArrowClassFactory.create("TRIANGLE")
    head = ArrowClass(width=10, height=10, offset=4)
    curve = LinkClass("ID_LINK_1", src, tgt, width=4, head=head)
    curve["FILL_COLOR"] = QColor(255, 0, 0)
    curve['BORDER_COLOR'] = QColor(255, 0, 0)
    curve["BORDER_WIDTH"] = 2

    LabelClass = LabelClassFactory.create("TEXT_LABEL")

    for (node, name) in [(src, "Source"), (tgt, "Target")]:
        label = LabelClass(node, name)
        label["FONT_SIZE"] = 10
        rect = label.boundingRect()
        label.setPos(-rect.width()/2, -rect.height()/2)
        _net.add_label(label)
        
    _net.add_link(curve)
    _net.add_node(src)
    _net.add_node(tgt)
        
    x0 = 400.0
    y0 = 400.0

    x1 = 600.0
    y1 = 400.0

    # A single arrow link with circle nodes
    NodeClass = NodeClassFactory.create("RECTANGLE_NODE")

    src = NodeClass('NODE_1', 50, 20, pos=QPoint(x1, y1))
    tgt = NodeClass('NODE_2', 50, 20, pos=QPoint(x0, y0))

    src["FILL_COLOR"] = Qt.blue
    tgt["FILL_COLOR"] = Qt.blue

    LinkClass = LinkClassFactory.create("CURVED_LINK")

    ArrowClass = ArrowClassFactory.create("HAMMER")
    head = ArrowClass(width=80, height=5, offset=4)
    curve = LinkClass("ID_LINK_2", src, tgt, width=4, head=head)
    curve["FILL_COLOR"] = QColor(255, 0, 0)
    curve['BORDER_COLOR'] = QColor(255, 0, 0)
    curve["BORDER_WIDTH"] = 2

    _net.add_link(curve)
    _net.add_node(src)
    _net.add_node(tgt)    
        
    nav.append_item(_net)
    