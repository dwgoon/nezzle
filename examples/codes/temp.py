from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF

from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import Network


def update(nav, net):
    net = Network("A single node with a label")
    node_colors = [Qt.red, Qt.green, Qt.blue]
    text_colors = [Qt.black, Qt.black, Qt.white]
    for i, name in enumerate(["A", "B", "C"]):
        node = EllipseNode(name, 40, 40, pos=QPointF(-80 + 80*i, -80 + 80*i))
        node['FILL_COLOR'] = node_colors[i]
        node["BORDER_COLOR"] = Qt.black
        node['BORDER_WIDTH'] = 2

        label = TextLabel(node, name)
        label["FONT_SIZE"] = 20
        label["TEXT_COLOR"] = text_colors[i]
        label.align()

        net.add_node(node)
        net.add_label(label)

        nav.append_item(net)
