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

    # A single arrow lins with circle nodes
    NodeClass = NodeClassFactory.create("RECT_NODE")

    src = NodeClass('ID_NODE_1', 50, 20, pos=QPoint(x1, y1))
    tgt = NodeClass('ID_NODE_2', 50, 20, pos=QPoint(x0, y0))

    src['FILL_COLOR'] = Qt.darkCyan
    tgt['FILL_COLOR'] = Qt.cyan

    LinkClass = LinkClassFactory.create("CURVED_LINK")

    HeaderClass = HeaderClassFactory.create('ARROW')
    header = HeaderClass(width=10, height=10, offset=4)
    curve = LinkClass("ID_LINK_1", src, tgt, width=4, header=header)
    curve['FILL_COLOR'] = QColor(255, 0, 0)
    curve['BORDER_COLOR'] = QColor(25, 50, 100)
    curve['BORDER_WIDTH'] = 2

    _net.add_link(curve)
    _net.add_node(src)
    _net.add_node(tgt)
        
    nav.append_item(_net)
    