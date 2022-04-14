from qtpy.QtCore import QPoint, Qt
from qtpy.QtGui import QColor

from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import EdgeClassFactory
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import Network


def update(nav, net):
    _net = Network('TestNetwork')

    x0 = 400.0
    y0 = 200.0

    x1 = 600.0
    y1 = 200.0

    # A single arrow edge with circle nodes
    NodeClass = NodeClassFactory.create("RECTANGLE_NODE")

    src = NodeClass('ID_NODE_1', 40, 20, pos=QPoint(x1, y1))
    trg = NodeClass('ID_NODE_2', 40, 20, pos=QPoint(x0, y0))

    src["FILL_COLOR"] = Qt.blue
    trg["FILL_COLOR"] = Qt.blue

    EdgeClass = EdgeClassFactory.create("CURVED_EDGE")

    ArrowClass = ArrowClassFactory.create("TRIANGLE")
    head = ArrowClass(width=10, height=10, offset=4)
    curve = EdgeClass("ID_EDGE_1", src, trg, width=4, head=head)
    curve["FILL_COLOR"] = QColor(255, 0, 0)
    curve['BORDER_COLOR'] = QColor(255, 0, 0)
    curve["BORDER_WIDTH"] = 2

    _net.add_edge(curve)
    _net.add_node(src)
    _net.add_node(trg)
        
    x0 = 400.0
    y0 = 400.0

    x1 = 600.0
    y1 = 400.0

    # A single arrow edge with circle nodes
    NodeClass = NodeClassFactory.create("RECTANGLE_NODE")

    src = NodeClass('ID_NODE_1', 50, 20, pos=QPoint(x1, y1))
    trg = NodeClass('ID_NODE_2', 50, 20, pos=QPoint(x0, y0))

    src["FILL_COLOR"] = Qt.blue
    trg["FILL_COLOR"] = Qt.blue

    EdgeClass = EdgeClassFactory.create("CURVED_EDGE")

    ArrowClass = ArrowClassFactory.create("HAMMER")
    head = ArrowClass(width=80, height=5, offset=4)
    curve = EdgeClass("ID_EDGE_2", src, trg, width=4, head=head)
    curve["FILL_COLOR"] = QColor(255, 0, 0)
    curve['BORDER_COLOR'] = QColor(255, 0, 0)
    curve["BORDER_WIDTH"] = 2

    _net.add_edge(curve)
    _net.add_node(src)
    _net.add_node(trg)    
        
    nav.append_item(_net)
    