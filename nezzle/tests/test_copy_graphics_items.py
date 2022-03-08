# -*- coding: utf-8 -*-

from qtpy import QtWidgets
from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.io import read_network
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import EdgeClassFactory
from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import Network

app = QtWidgets.QApplication([])


def test_copy_node():
    NodeClass = NodeClassFactory.create("CIRCLE_NODE")
    n1 = NodeClass("ID1", 5, pos=QPointF(10, -20))
    n1["FILL_COLOR"] = '#FFEEAA'
    n2 = n1.copy()

    assert n1.iden == n2.iden
    assert n1["FILL_COLOR"] == n2["FILL_COLOR"]
    assert n1.pos() == n2.pos()
    assert n1.to_dict() == n2.to_dict()

    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
    n1 = NodeClass("ID1", 100, 20, pos=QPointF(10, -20))
    n1["FILL_COLOR"] = Qt.black
    n2 = n1.copy()

    assert n1.iden == n2.iden
    assert n1["FILL_COLOR"] == n2["FILL_COLOR"]
    assert n1.pos() == n2.pos()
    assert n1.to_dict() == n2.to_dict()


def test_copy_edge():

    net = Network("ID_NETWORK")

    NodeClass = NodeClassFactory.create("CIRCLE_NODE")
    n1 = NodeClass("ID1", 5, pos=QPointF(10, -20))
    n2 = NodeClass("ID2", 5, pos=QPointF(10, 20))
    net.add_node(n1)
    net.add_node(n2)

    ArrowClass = ArrowClassFactory.create("TRIANGLE")
    head = ArrowClass()

    EdgeClass = EdgeClassFactory.create('CURVED_EDGE')
    edge1 = EdgeClass(iden="ID3", source=n1, target=n2, width=3, head=head)
    edge1["FILL_COLOR"] = QColor(10, 100, 10)
    edge1['WIDTH'] = 5

    edge2 = edge1.copy()

    net.add_edge(edge1)
    net.add_edge(edge2)

    assert edge1.iden == edge2.iden
    assert edge1.source == edge2.source
    assert edge1.target == edge2.target
    assert edge1["FILL_COLOR"] == edge2["FILL_COLOR"]
    assert edge1['WIDTH'] == edge2['WIDTH']
    assert edge1.to_dict() == edge2.to_dict()


def test_copy_label():
    NodeClass = NodeClassFactory.create("CIRCLE_NODE")
    n1 = NodeClass("ID1", 5, pos=QPointF(10, -20))

    LabelClass = LabelClassFactory.create("TEXT_LABEL")
    label1 = LabelClass(parent=n1, text="This is text labels")
    label2 = label1.copy()

    assert label1.text == label2.text
    assert label1.font.toString() == label2.font.toString()
    assert label1.pos() == label2.pos()
    assert label1.to_dict() == label2.to_dict()


def test_copy_network():
    net1 = read_network("jkwon_egfr_pathway.sif")
    net2 = net1.copy()

    assert set(net1.nodes.keys()) == set(net2.nodes.keys())
    assert set(net1.edges.keys()) == set(net2.edges.keys())
    assert net1.to_dict() == net2.to_dict()
