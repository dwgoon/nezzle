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

from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import EdgeClassFactory
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

    # A single arrow edge with circle nodes
    NodeClass = NodeClassFactory.create("RECTANGLE_NODE")

    src = NodeClass('ID_NODE_1', 50, 20, pos=QPoint(x1, y1))
    trg = NodeClass('ID_NODE_2', 50, 20, pos=QPoint(x0, y0))

    src["FILL_COLOR"] = Qt.darkCyan
    trg["FILL_COLOR"] = Qt.cyan

    EdgeClass = EdgeClassFactory.create("CURVED_EDGE")

    ArrowClass = ArrowClassFactory.create("TRIANGLE")
    head = ArrowClass(width=10, height=10, offset=4)
    curve = EdgeClass("ID_EDGE_1", src, trg, width=4, head=head)
    curve["FILL_COLOR"] = QColor(255, 0, 0)
    curve['BORDER_COLOR'] = QColor(25, 50, 100)
    curve["BORDER_WIDTH"] = 2

    net.add_edge(curve)
    net.add_node(src)
    net.add_node(trg)

    #
    #
    # # Two-nodes negative feedback loop
    # NodeClass = NodeClassFactory.create('ELLIPSE_NODE')
    # ArrowClass = ArrowClassFactory.create("HAMMER")
    # head = ArrowClass(width=16, height=4, offset=4)
    # src = NodeClass('ID_NODE_3', 30, 20, pos=QPoint(x0, y0 + 20))
    # trg = NodeClass('ID_NODE_4', 20, 30, pos=QPoint(x1, y1 + 20))
    #
    # src["FILL_COLOR"] = QColor(100, 50, 150, 50)
    # src['BORDER_COLOR'] = Qt.red
    # src["BORDER_WIDTH"] = 2
    # src['BORDER_LINE_TYPE'] = Qt.DotLine
    # trg["FILL_COLOR"] = QColor(100, 50, 150, 50)
    # trg['BORDER_COLOR'] = Qt.yellow
    # trg["BORDER_WIDTH"] = 2
    # trg['BORDER_LINE_TYPE'] = 'DASH'
    #
    # curve = EdgeClass("ID_EDGE_2", src, trg, width=4, head=head)
    # curve["FILL_COLOR"] = QColor(0, 0, 255)
    # curve['BORDER_COLOR'] = '#ffa500'
    #
    # net.add_edge(curve)
    #
    # ArrowClass = ArrowClassFactory.create("TRIANGLE")
    # head = ArrowClass(width=10, height=10, offset=4)
    # curve = EdgeClass("ID_EDGE_3", trg, src, width=2, head=head)
    # curve["FILL_COLOR"] = QColor(0, 0, 255)
    # curve["BORDER_WIDTH"] = 1
    # curve['BORDER_COLOR'] = QColor(255, 0, 0)
    # curve['BORDER_JOIN'] = 'ROUND'
    #
    # net.add_edge(curve)
    # net.add_node(src)
    # net.add_node(trg)
    #
    # src = NodeClass('ID_NODE_5', 20, 40, pos=QPoint(x0, y0 - 50))
    # trg = NodeClass('ID_NODE_6', 20, 40, pos=QPoint(x1, y1 - 50))
    #
    # src["FILL_COLOR"] = Qt.green
    # src['BORDER_COLOR'] = Qt.magenta
    # src["BORDER_WIDTH"] = 3
    # trg["FILL_COLOR"] = Qt.blue
    # trg['BORDER_COLOR'] = Qt.magenta
    # trg.pen = QPen()  # Previously defined border options are ignored
    #
    # curve = EdgeClass("ID_EDGE_4", trg, src, width=4, head=None)
    # curve["FILL_COLOR"] = QColor(25, 150, 155)
    #
    # EdgeClass = EdgeClassFactory.create("STRAIGHT_EDGE")
    # ArrowClass = ArrowClassFactory.create("TRIANGLE")
    # head = ArrowClass(width=10, height=10, offset=4)
    # straight = EdgeClass("ID_EDGE_5", src, trg, width=4, head=head)
    # straight["FILL_COLOR"] = Qt.magenta
    # net.add_edge(straight)
    #
    # net.add_edge(curve)
    # net.add_node(src)
    # net.add_node(trg)
    #
    # LabelClass = LabelClassFactory.create("TEXT_LABEL")
    # labels = LabelClass(src, "NODE_5")
    # labels['TEXT_COLOR'] = Qt.red
    # labels['FONT_BOLD'] = True
    # labels['FONT_ITALIC'] = True
    # labels['FONT_SIZE'] = 14
    # labels['FONT_FAMILY'] = 'Times New Roman'
    # net.add_label(labels)
    #
    # labels = LabelClass(curve, "I am EDGE_4")
    # labels['TEXT_COLOR'] = Qt.blue
    # labels['FONT_SIZE'] = 20
    # labels['FONT_FAMILY'] = 'Tahoma'
    # net.add_label(labels)
    #
    # # Create arrow headed selfloop edge for a circle nodes
    # nodes = NodeClass('ID_NODE_7', 100, 100, pos=QPoint(x0, y0 - 100))
    # nodes["FILL_COLOR"] = QColor(100, 150, 150, 100)
    #
    # ArrowClass = ArrowClassFactory.create("TRIANGLE")
    # head = ArrowClass(width=10, height=10, offset=4)
    #
    # EdgeClass = EdgeClassFactory.create("SELFLOOP_EDGE")
    # edge = EdgeClass('ID_EDGE_6', nodes, width=6, head=head)
    # #edge["BORDER_WIDTH"] = 2
    # #edge['BORDER_COLOR'] = QColor(255, 100, 100, 200)
    # edge["FILL_COLOR"] = QColor(100, 100, 255, 100)
    # net.add_edge(edge)
    # net.add_node(nodes)
    #
    # # Create hammer headed selfloop edge for ellipse nodes (width-major)
    # nodes = NodeClass('ID_NODE_7', 100, 80, pos=QPoint(x0-20, y0-100))
    # nodes["FILL_COLOR"] = QColor(200, 200, 255, 100)
    #
    # ArrowClass = ArrowClassFactory.create("HAMMER")
    # head = ArrowClass(width=14, height=4, offset=4)
    #
    # EdgeClass = EdgeClassFactory.create("SELFLOOP_EDGE")
    # edge = EdgeClass('ID_EDGE_7', nodes, width=6, head=head)
    # #edge["BORDER_WIDTH"] = 2
    # #edge['BORDER_COLOR'] = QColor(200, 200, 255, 150)
    # edge["FILL_COLOR"] = QColor(255, 100, 100, 250)
    # net.add_edge(edge)
    # net.add_node(nodes)
    #
    # # Create arrow headed selfloop edge for ellipse nodes (width-major)
    # nodes = NodeClass('ID_NODE_8', 40, 30, pos=QPoint(x0 - 40, y0 - 150))
    # nodes["FILL_COLOR"] = QColor(100, 255, 100, 200)
    #
    # ArrowClass = ArrowClassFactory.create("TRIANGLE")
    # head = ArrowClass(width=5, height=5, offset=4)
    #
    # EdgeClass = EdgeClassFactory.create("SELFLOOP_EDGE")
    # edge = EdgeClass('ID_EDGE_8', nodes, width=2, head=head)
    # #edge["BORDER_WIDTH"] = 1
    # #edge['BORDER_COLOR'] = QColor(200, 200, 255, 150)
    # edge["FILL_COLOR"] = QColor(255, 100, 100, 250)
    # net.add_edge(edge)
    # net.add_node(nodes)
    #
    #
    # # Create hammer headed selfloop edge for ellipse nodes (height-major)
    # nodes = NodeClass('ID_NODE_9', 80, 100, pos=QPoint(x0-40, y0-120))
    # nodes["FILL_COLOR"] = QColor(200, 200, 255, 100)
    #
    # ArrowClass = ArrowClassFactory.create("HAMMER")
    # head = ArrowClass(width=14, height=4, offset=2)
    #
    # EdgeClass = EdgeClassFactory.create("SELFLOOP_EDGE")
    # edge = EdgeClass('ID_EDGE_10', nodes, width=6, head=head)
    #
    # edge["FILL_COLOR"] = QColor(255, 150, 150, 250)
    # net.add_edge(edge)
    # net.add_node(nodes)
    #
    # # Create arrow headed selfloop edge for ellipse nodes (height-major)
    # nodes = NodeClass('ID_NODE_10', 20, 40, pos=QPoint(x0 - 80, y0 - 180))
    # nodes["FILL_COLOR"] = QColor(200, 255, 200, 200)
    #
    # ArrowClass = ArrowClassFactory.create("TRIANGLE")
    # head = ArrowClass(width=5, height=5, offset=2)
    #
    # EdgeClass = EdgeClassFactory.create("SELFLOOP_EDGE")
    # edge = EdgeClass('ID_EDGE_11', nodes, width=2, head=head)
    #
    # edge["FILL_COLOR"] = QColor(255, 100, 100, 250)
    # net.add_edge(edge)
    # net.add_node(nodes)

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