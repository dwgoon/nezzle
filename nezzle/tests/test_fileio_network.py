# [DEPRECATED TESTS]

from qtpy import QtWidgets
from qtpy.QtGui import QColor
from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import EdgeClassFactory
from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import Network

from nezzle.io import read_network

app = QtWidgets.QApplication([])

# def test_json_network():
#
#     a = NodeClass("NODE_A", "A",
#                   QColor(1, 20, 200, 10),
#                   radius=5,
#                   pos=QPointF(100, 100))
#
#     b = NodeClass("NODE_B", "B",
#                   QColor(200, 20, 1, 10),
#                   radius=7,
#                   pos=QPointF(200, 200))
#
#     edge_ab = ArrowEdge("EDGE_AB", a, b, 2, QColor(0, 0, 0, 0), '+')
#     edge_ba = HammerEdge("EDGE_BA", b, a, 3, QColor(Qt.red), '-')
#
#     net = Network()
#
#     net.add_node(a)
#     net.add_node(b)
#
#     net.add_edge(edge_ab)
#     net.add_edge(edge_ba)
#
#     with open("_test_json_network.json", "wt") as fout:
#         fout.write(json.dumps(net.toDict()))
#
#     with open("_test_json_network.json", "rt") as fin:
#         d = json.loads(fin.read())
#
#     print("After reading from JSON")
#     net2 = Network.fromDict(d)
#
#     assert net2.to_dict() == net.toDict()
#     os.remove("_test_json_network.json")


def test_create_network():
    # Test creating network
    net = Network('ID_NETWORK')

    # Test CircleNode
    NodeClass = NodeClassFactory.create("CIRCLE_NODE")

    node = NodeClass('ID_NODE_1', 30, pos=QPointF(100, 100))
    net.add_node(node)
    node["FILL_COLOR"] = QColor(100, 50, 150, 100)
    node['BORDER_COLOR'] = Qt.red
    node["BORDER_WIDTH"] = 2
    node['BORDER_LINE_TYPE'] = Qt.DotLine
    attr = node.to_dict()

    node2 = NodeClass.from_dict(attr)
    node2['POS_X'] = -100
    node2['POS_Y'] = -300
    node2.iden = 'ID_NODE_2'
    net.add_node(node2)

    assert node2.iden == node2['ID']

    # Test EllipseNode
    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")

    node3 = NodeClass('ID_NODE_3', 30, 50, pos=QPointF(-100, 100))
    net.add_node(node3)

    node4 = NodeClass.from_dict(node3.to_dict())
    net.add_node(node4)
    assert node3.to_dict() == node4.to_dict()

    node4.iden = 'ID_NODE_4'
    node4.setX(-300)
    node4.setY(200)

    assert node4.x() == node4['POS_X']
    assert node4.y() == node4['POS_Y']

    node4['POS_X'] = 1000
    node4['POS_Y'] = 2000

    assert node4.x() == node4['POS_X']
    assert node4.y() == node4['POS_Y']

    assert node3.to_dict() != node4.to_dict()

    # Create CurvedEdge
    ArrowClass = ArrowClassFactory.create("TRIANGLE")
    head = ArrowClass()
    EdgeClass = EdgeClassFactory.create('CURVED_EDGE')
    edge = EdgeClass('ID_EDGE_1', node, node2, head=head)
    net.add_edge(edge)
    attr = edge.to_dict()

    edge2 = EdgeClass.from_dict(attr, node, node2)
    edge2.iden = 'ID_EDGE_2'
    net.add_edge(edge2)

    # Create StraightEdge
    ArrowClass = ArrowClassFactory.create("HAMMER")
    head = ArrowClass()
    EdgeClass = EdgeClassFactory.create('STRAIGHT_EDGE')
    edge3 = EdgeClass('ID_EDGE_3', node, node2, head=head)
    net.add_edge(edge3)

    ArrowClass = ArrowClassFactory.create("TRIANGLE")
    head = ArrowClass()
    edge4 = EdgeClass.from_dict(edge3.to_dict(), node, node2)
    edge4.iden = 'ID_EDGE_4'
    edge4.head = head
    net.add_edge(edge4)

    # Setting the size of CircleNode
    node2.width = 100
    node2.height = 200
    assert node2.width == node2.height == 2*node2.radius

    node2.radius = 25
    assert node2.width == node2.height == 2*node2.radius

    # Test creating font
    LabelClass = LabelClassFactory.create("TEXT_LABEL")
    label = LabelClass(node, "This is labels")
    label.iden = 'LABEL_1'
    net.add_label(label)
    label['TEXT_COLOR'] = Qt.red
    label['FONT_BOLD'] = True
    label['FONT_ITALIC'] = True
    label['FONT_SIZE'] = 14
    label['FONT_FAMILY'] = 'Times New Roman'
    label2 = LabelClass.from_dict(label.to_dict(), node)
    label2.iden = 'LABEL_2'

    # Test converting networks
    dict_net = net.to_dict()
    net2 = net.from_dict(dict_net)
    dict_net2 = net2.to_dict()

    assert dict_net['ID'] == dict_net2['ID']
    assert dict_net['NAME'] == dict_net2['NAME']
    assert dict_net['NEZZLE_VERSION'] == dict_net2['NEZZLE_VERSION']
    assert dict_net['BACKGROUND_COLOR'] == dict_net2['BACKGROUND_COLOR']
    assert len(dict_net["NODES"]) == len(dict_net2["NODES"])
    assert len(dict_net["EDGES"]) == len(dict_net2["EDGES"])
    assert len(dict_net["LABELS"]) == len(dict_net2["LABELS"])

def test_json_jkwon():
    net1 = read_network("jkwon_egfr_pathway.sif")
    io.write_network(net1, "jkwon_egfr_pathway.json")
    net2 = read_network("jkwon_egfr_pathway.json")

    assert set(net1.nodes.keys()) == set(net2.nodes.keys())
    assert set(net1.edges.keys()) == set(net2.edges.keys())
    assert net1.to_dict() == net2.to_dict()


def test_json_korkut_2015():
    net1 = read_network("korkut_2015.json")
    io.write_network(net1, "korkut_2015_02.json")
    net2 = read_network("korkut_2015_02.json")

    assert set(net1.nodes.keys()) == set(net2.nodes.keys())
    assert set(net1.edges.keys()) == set(net2.edges.keys())
    assert net1.to_dict() == net2.to_dict()

if __name__ == '__main__':

    test_create_network()
    test_json_jkwon()