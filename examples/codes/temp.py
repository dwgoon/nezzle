import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import Network


def update(ntv, net):
    color_white = np.array([255, 255, 255, 0])
    color_up = np.array([255, 0, 0, 0])
    color_dn = np.array([0, 0, 255, 0])

    num_nodes = 30

    x = np.random.uniform(-200, 200, num_nodes)
    y = np.random.uniform(-200, 200, num_nodes)
    z = np.random.uniform(-1, 1, num_nodes)
    abs_z = np.abs(z)
    norm_abs_z = abs_z / abs_z.max()

    net = Network("Node color mapping")
    for i in range(num_nodes):
        name = str(i)
        node = EllipseNode(name, 40, 40, pos=QPointF(x[i], y[i]))

        if z[i] > 0:
            color = color_white + norm_abs_z[i] * (color_up - color_white)
        elif z[i] <= 0:
            color = color_white + norm_abs_z[i] * (color_dn - color_white)

        color[3] = 255
        node['FILL_COLOR'] = QColor(*color)
        node["BORDER_COLOR"] = Qt.black
        node['BORDER_WIDTH'] = 2

        label_name = TextLabel(node, name)
        label_name["FONT_SIZE"] = 16
        label_name["TEXT_COLOR"] = Qt.white
        label_name.align()

        lightness = QColor(node['FILL_COLOR']).lightness()
        if lightness < 200:
            label_name['TEXT_COLOR'] = Qt.white
            label_name['FONT_BOLD'] = True
        else:
            label_name['TEXT_COLOR'] = Qt.black
            label_name['FONT_BOLD'] = False

        net.add_node(node)
        net.add_label(label_name)
    # end of for
    nav.append_item(net)
