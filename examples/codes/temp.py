from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF

from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import Network


def update(nav, net):
    net = Network("A single node with a label")

    node = EllipseNode("NODE", 40, 40, pos=QPointF(0, 0))
    node['FILL_COLOR'] = Qt.yellow
    node["BORDER_COLOR"] = Qt.black
    node['BORDER_WIDTH'] = 2

    label = TextLabel(node, "A")
    label["FONT_SIZE"] = 20
    label["TEXT_COLOR"] = Qt.black
    label.align()

    net.add_node(node)
    net.add_label(label)

    nav.append_item(net)
