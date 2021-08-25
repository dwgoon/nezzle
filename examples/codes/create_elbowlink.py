import os
import networkx as nx
import numpy as np

from qtpy.QtWidgets import QApplication
from qtpy.QtCore import QPoint, Qt
from qtpy.QtGui import QColor
from qtpy.QtGui import QPen

from nezzle.graphics import HeaderClassFactory
from nezzle.graphics import LinkClassFactory
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import GraphicsView
from nezzle.graphics import GraphicsScene
from nezzle.graphics import Network
from nezzle.fileio import write_image

def update(nav, net):
    _net = Network('TestNetwork')

    x0 = 400.0
    y0 = 200.0

    x1 = 600.0
    y1 = 200.0

    # A single arrow link with circle nodes
    NodeClass = NodeClassFactory.create("RECT_NODE")

    src = NodeClass('source1', 80, 40, pos=QPoint(x1, y1))
    tgt = NodeClass('target1', 80, 40, pos=QPoint(x0, y0))

    src['FILL_COLOR'] = QColor(100, 100, 200) #, 100) #Qt.cyan
    tgt['FILL_COLOR'] = QColor(100, 100, 200) #, 100) #Qt.cyan

    LinkClass = LinkClassFactory.create("VERTICAL_ELBOW_LINK")

    HeaderClass = HeaderClassFactory.create('ARROW')
    header = HeaderClass(width=10, height=10, offset=4)
    #header = None

    elbow = LinkClass("LINK_1", src, tgt, width=4, header=header)
    elbow['FILL_COLOR'] = QColor(255, 0, 0)
    elbow['BORDER_COLOR'] = QColor(255, 0, 0)
    elbow['BORDER_WIDTH'] = 2

    LabelClass = LabelClassFactory.create("TEXT_LABEL")

    for (node, name) in [(src, "Source1"), (tgt, "Target1")]:
        label = LabelClass(node, name)
        label["FONT_SIZE"] = 10
        rect = label.boundingRect()
        label.setPos(-rect.width()/2, -rect.height()/2)
        _net.add_label(label)
        
    _net.add_link(elbow)
    _net.add_node(src)
    _net.add_node(tgt)
        
    x0 = 400.0
    y0 = 400.0

    x1 = 600.0
    y1 = 400.0

    # A single arrow link with circle nodes
    NodeClass = NodeClassFactory.create("RECT_NODE")

    src = NodeClass('source2', 80, 40, pos=QPoint(x1, y1))
    tgt = NodeClass('target2', 80, 40, pos=QPoint(x0, y0))

    src['FILL_COLOR'] = QColor(100, 150, 100) #, 100)  # Qt.cyan
    tgt['FILL_COLOR'] = QColor(100, 150, 100) #, 100)  # Qt.cyan

    LinkClass = LinkClassFactory.create("HORIZONTAL_ELBOW_LINK")

    HeaderClass = HeaderClassFactory.create('ARROW')
    header = HeaderClass(width=10, height=10, offset=4)
    # header = None

    elbow = LinkClass("LINK_2", src, tgt, width=4, header=header)
    elbow['FILL_COLOR'] = QColor(255, 0, 0)
    elbow['BORDER_COLOR'] = QColor(255, 0, 0)
    elbow['BORDER_WIDTH'] = 2

    LabelClass = LabelClassFactory.create("TEXT_LABEL")

    for (node, name) in [(src, "Source2"), (tgt, "Target2")]:
        label = LabelClass(node, name)
        label["FONT_SIZE"] = 10
        rect = label.boundingRect()
        label.setPos(-rect.width() / 2, -rect.height() / 2)
        _net.add_label(label)

    _net.add_link(elbow)
    _net.add_node(src)
    _net.add_node(tgt)

    nav.append_item(_net)
    