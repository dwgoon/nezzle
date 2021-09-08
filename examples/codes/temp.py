from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import RectangleNode
from nezzle.graphics import TextLabel
from nezzle.graphics import Network


def update(nav, net):
    net = Network("Five rectangle nodes of different sizes")
    num_nodes = 5
    for i in range(num_nodes):
        name = str(i)
        node = RectangleNode(name,
                             20 + 10*i,
                             40,
                             pos=QPointF(-200 + 80*i, 100 - 20*i))
        node['FILL_COLOR'] = QColor(153, 51, 0)
        node["BORDER_COLOR"] = Qt.black
        node['BORDER_WIDTH'] = 2

        label = TextLabel(node, name)
        label["FONT_SIZE"] = 16 + 2*i
        label["TEXT_COLOR"] = Qt.white
        label.align()

        net.add_node(node)
        net.add_label(label)

    nav.append_item(net)
