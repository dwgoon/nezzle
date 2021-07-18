# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 19:29:49 2017

@author: dwlee
"""

from sys import argv

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


def add_curve(view):

    net = Network('TestNetwork')
    scene = net.scene
    #scene.setSceneRect(0, 0, 1000, 1000)
    view.setScene(scene)

    x0 = 400.0
    y0 = 200.0

    x1 = 600.0
    y1 = 200.0

    # A single arrow link with circle nodes
    NodeClass = NodeClassFactory.create("CIRCLE_NODE")

    src = NodeClass('ID_NODE_1', 20, pos=QPoint(x1, y1))
    tgt = NodeClass('ID_NODE_2', 20, pos=QPoint(x0, y0))

    src['FILL_COLOR'] = Qt.darkCyan
    tgt['FILL_COLOR'] = Qt.cyan

    LinkClass = LinkClassFactory.create("CURVED_LINK")

    HeaderClass = HeaderClassFactory.create('ARROW')
    header = HeaderClass(width=10, height=10, offset=4)
    curve = LinkClass("ID_LINK_1", src, tgt, width=4, header=header)
    curve['FILL_COLOR'] = QColor(255, 0, 0)
    curve['BORDER_COLOR'] = QColor(25, 50, 100)
    curve['BORDER_WIDTH'] = 2

    net.add_link(curve)
    net.add_node(src)
    net.add_node(tgt)


    # Two-node negative feedback loop
    NodeClass = NodeClassFactory.create('ELLIPSE_NODE')
    HeaderClass = HeaderClassFactory.create('HAMMER')
    header = HeaderClass(width=16, height=4, offset=4)
    src = NodeClass('ID_NODE_3', 30, 20, pos=QPoint(x0, y0 + 20))
    tgt = NodeClass('ID_NODE_4', 20, 30, pos=QPoint(x1, y1 + 20))

    src['FILL_COLOR'] = QColor(100, 50, 150, 50)
    src['BORDER_COLOR'] = Qt.red
    src['BORDER_WIDTH'] = 2
    src['BORDER_LINE_TYPE'] = Qt.DotLine
    tgt['FILL_COLOR'] = QColor(100, 50, 150, 50)
    tgt['BORDER_COLOR'] = Qt.yellow
    tgt['BORDER_WIDTH'] = 2
    tgt['BORDER_LINE_TYPE'] = 'DASH'

    curve = LinkClass("ID_LINK_2", src, tgt, width=4, header=header)
    curve['FILL_COLOR'] = QColor(0, 0, 255)
    curve['BORDER_COLOR'] = '#ffa500'

    net.add_link(curve)

    HeaderClass = HeaderClassFactory.create('ARROW')
    header = HeaderClass(width=10, height=10, offset=4)
    curve = LinkClass("ID_LINK_3", tgt, src, width=2, header=header)
    curve['FILL_COLOR'] = QColor(0, 0, 255)
    curve['BORDER_WIDTH'] = 1
    curve['BORDER_COLOR'] = QColor(255, 0, 0)
    curve['BORDER_JOIN'] = 'ROUND'

    net.add_link(curve)
    net.add_node(src)
    net.add_node(tgt)

    src = NodeClass('ID_NODE_5', 20, 40, pos=QPoint(x0, y0 - 50))
    tgt = NodeClass('ID_NODE_6', 20, 40, pos=QPoint(x1, y1 - 50))

    src['FILL_COLOR'] = Qt.green
    src['BORDER_COLOR'] = Qt.magenta
    src['BORDER_WIDTH'] = 3
    tgt['FILL_COLOR'] = Qt.blue
    tgt['BORDER_COLOR'] = Qt.magenta
    tgt.pen = QPen()  # Previously defined border options are ignored

    curve = LinkClass("ID_LINK_4", tgt, src, width=4, header=None)
    curve['FILL_COLOR'] = QColor(25, 150, 155)

    LinkClass = LinkClassFactory.create("STRAIGHT_LINK")
    HeaderClass = HeaderClassFactory.create('ARROW')
    header = HeaderClass(width=10, height=10, offset=4)
    straight = LinkClass("ID_LINK_5", src, tgt, width=4, header=header)
    straight['FILL_COLOR'] = Qt.magenta
    net.add_link(straight)

    net.add_link(curve)
    net.add_node(src)
    net.add_node(tgt)

    LabelClass = LabelClassFactory.create("TEXT_LABEL")
    label = LabelClass(src, "NODE_5")
    label['TEXT_COLOR'] = Qt.red
    label['FONT_BOLD'] = True
    label['FONT_ITALIC'] = True
    label['FONT_SIZE'] = 14
    label['FONT_FAMILY'] = 'Times New Roman'
    net.add_label(label)

    label = LabelClass(curve, "I am LINK_4")
    label['TEXT_COLOR'] = Qt.blue
    label['FONT_SIZE'] = 20
    label['FONT_FAMILY'] = 'Tahoma'
    net.add_label(label)

    # Create arrow headed selfloop link for a circle node
    node = NodeClass('ID_NODE_7', 100, 100, pos=QPoint(x0, y0 - 100))
    node['FILL_COLOR'] = QColor(100, 150, 150, 100)

    HeaderClass = HeaderClassFactory.create('ARROW')
    header = HeaderClass(width=10, height=10, offset=4)

    LinkClass = LinkClassFactory.create("SELFLOOP_LINK")
    link = LinkClass('ID_LINK_6', node, width=6, header=header)
    #link['BORDER_WIDTH'] = 2
    #link['BORDER_COLOR'] = QColor(255, 100, 100, 200)
    link['FILL_COLOR'] = QColor(100, 100, 255, 100)
    net.add_link(link)
    net.add_node(node)

    # Create hammer headed selfloop link for ellipse node (width-major)
    node = NodeClass('ID_NODE_7', 100, 80, pos=QPoint(x0-20, y0-100))
    node['FILL_COLOR'] = QColor(200, 200, 255, 100)

    HeaderClass = HeaderClassFactory.create('HAMMER')
    header = HeaderClass(width=14, height=4, offset=4)

    LinkClass = LinkClassFactory.create("SELFLOOP_LINK")
    link = LinkClass('ID_LINK_7', node, width=6, header=header)
    #link['BORDER_WIDTH'] = 2
    #link['BORDER_COLOR'] = QColor(200, 200, 255, 150)
    link['FILL_COLOR'] = QColor(255, 100, 100, 250)
    net.add_link(link)
    net.add_node(node)

    # Create arrow headed selfloop link for ellipse node (width-major)
    node = NodeClass('ID_NODE_8', 40, 30, pos=QPoint(x0 - 40, y0 - 150))
    node['FILL_COLOR'] = QColor(100, 255, 100, 200)

    HeaderClass = HeaderClassFactory.create('ARROW')
    header = HeaderClass(width=5, height=5, offset=4)

    LinkClass = LinkClassFactory.create("SELFLOOP_LINK")
    link = LinkClass('ID_LINK_8', node, width=2, header=header)
    #link['BORDER_WIDTH'] = 1
    #link['BORDER_COLOR'] = QColor(200, 200, 255, 150)
    link['FILL_COLOR'] = QColor(255, 100, 100, 250)
    net.add_link(link)
    net.add_node(node)


    # Create hammer headed selfloop link for ellipse node (height-major)
    node = NodeClass('ID_NODE_9', 80, 100, pos=QPoint(x0-40, y0-120))
    node['FILL_COLOR'] = QColor(200, 200, 255, 100)

    HeaderClass = HeaderClassFactory.create('HAMMER')
    header = HeaderClass(width=14, height=4, offset=2)

    LinkClass = LinkClassFactory.create("SELFLOOP_LINK")
    link = LinkClass('ID_LINK_10', node, width=6, header=header)

    link['FILL_COLOR'] = QColor(255, 150, 150, 250)
    net.add_link(link)
    net.add_node(node)

    # Create arrow headed selfloop link for ellipse node (height-major)
    node = NodeClass('ID_NODE_10', 20, 40, pos=QPoint(x0 - 80, y0 - 180))
    node['FILL_COLOR'] = QColor(200, 255, 200, 200)

    HeaderClass = HeaderClassFactory.create('ARROW')
    header = HeaderClass(width=5, height=5, offset=2)

    LinkClass = LinkClassFactory.create("SELFLOOP_LINK")
    link = LinkClass('ID_LINK_11', node, width=2, header=header)

    link['FILL_COLOR'] = QColor(255, 100, 100, 250)
    net.add_link(link)
    net.add_node(node)

if __name__ == '__main__':
    app = QApplication(argv)
    #view = View()
    #view.setWindowTitle('MainWindow')
    #view.show()

    view = GraphicsView()
    add_curve(view)
    view.setWindowTitle('Testing nezzle functionality')
    view.show()
    app.exec_()