from qtpy.QtCore import QPoint
from qtpy.QtGui import QColor

from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import EdgeClassFactory
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import Network


def update(nav, net):
    _net = Network('TestNetwork')

    x0 = 400.0
    y0 = 200.0

    x1 = 600.0
    y1 = 200.0

    # A single arrow edge with circle nodes
    NodeClass = NodeClassFactory.create("RECTANGLE_NODE")

    src = NodeClass('source1', 80, 40, pos=QPoint(x1, y1))
    trg = NodeClass('target1', 80, 40, pos=QPoint(x0, y0))

    src["FILL_COLOR"] = QColor(100, 100, 200) #, 100) #Qt.cyan
    trg["FILL_COLOR"] = QColor(100, 100, 200) #, 100) #Qt.cyan

    EdgeClass = EdgeClassFactory.create("VERTICAL_ELBOW_EDGE")

    ArrowClass = ArrowClassFactory.create("TRIANGLE")
    head = ArrowClass(width=10, height=10, offset=4)
    #head = None

    elbow = EdgeClass("EDGE_1", src, trg, width=4, head=head)
    elbow["FILL_COLOR"] = QColor(255, 0, 0)
    elbow['BORDER_COLOR'] = QColor(255, 0, 0)
    elbow["BORDER_WIDTH"] = 2

    LabelClass = LabelClassFactory.create("TEXT_LABEL")

    for (node, name) in [(src, "Source1"), (trg, "Target1")]:
        label = LabelClass(node, name)
        label["FONT_SIZE"] = 10
        rect = label.boundingRect()
        label.setPos(-rect.width()/2, -rect.height()/2)
        _net.add_label(label)
        
    _net.add_edge(elbow)
    _net.add_node(src)
    _net.add_node(trg)
        
    x0 = 400.0
    y0 = 400.0

    x1 = 600.0
    y1 = 400.0

    # A single arrow edge with circle nodes
    NodeClass = NodeClassFactory.create("RECTANGLE_NODE")

    src = NodeClass('source2', 80, 40, pos=QPoint(x1, y1))
    trg = NodeClass('target2', 80, 40, pos=QPoint(x0, y0))

    src["FILL_COLOR"] = QColor(100, 150, 100) #, 100)  # Qt.cyan
    trg["FILL_COLOR"] = QColor(100, 150, 100) #, 100)  # Qt.cyan

    EdgeClass = EdgeClassFactory.create("HORIZONTAL_ELBOW_EDGE")

    ArrowClass = ArrowClassFactory.create("TRIANGLE")
    head = ArrowClass(width=10, height=10, offset=4)
    # head = None

    elbow = EdgeClass("EDGE_2", src, trg, width=4, head=head)
    elbow["FILL_COLOR"] = QColor(255, 0, 0)
    elbow['BORDER_COLOR'] = QColor(255, 0, 0)
    elbow["BORDER_WIDTH"] = 2

    LabelClass = LabelClassFactory.create("TEXT_LABEL")

    for (node, name) in [(src, "Source2"), (trg, "Target2")]:
        label = LabelClass(node, name)
        label["FONT_SIZE"] = 10
        rect = label.boundingRect()
        label.setPos(-rect.width() / 2, -rect.height() / 2)
        _net.add_label(label)

    _net.add_edge(elbow)
    _net.add_node(src)
    _net.add_node(trg)

    nav.append_item(_net)
    