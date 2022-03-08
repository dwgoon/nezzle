import os
import os.path as osp

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import EllipseNode
from nezzle.graphics import StraightEdge
from nezzle.graphics import Triangle
from nezzle.graphics import Network
from nezzle.io import write_image


def add_node(net, iden, x, y):
    node = EllipseNode(iden, 40, 40, pos=QPointF(x, y))

    node["FILL_COLOR"] = Qt.green
    node["BORDER_COLOR"] = Qt.black
    node["BORDER_WIDTH"] = 4

    net.add_node(node)
    return node


def add_edges(net, neurons, l):
    """Connect (l-1)-th layer to l-th layer.

    Args:
        layers: the number of neurons in each layer.
        l: layer number (l-th layer).
    """
    if l < 1:
        return

    for src in neurons[l - 1]:
        for tgt in neurons[l]:
            head = Triangle(width=12, height=12, offset=8)
            iden = "%s-%s"%(src.iden, tgt.iden)
            edge = StraightEdge(iden, src, tgt, width=4, head=head)
            edge["FILL_COLOR"] = QColor(0, 0, 0, 50)
            net.add_edge(edge)


def create_network(layers, r=40, vs=40, hs=200, op=(0, 0)):
    """Create a fully-connected neural network without activation functions.

    Args:
        layers: the number of neurons in each layer.
        r: node radius for a single neuron.
        vs: vertical space between neurons.
        hs: horizontal space between neurons.
    """

    neurons = [[] for _ in range(len(layers))]

    net = Network("Neural network")

    ox, oy = op
    for l, nn in enumerate(layers):
        # l: l-th layer
        # nn: the number of neurons in l-th layer.
        x = ox + l * (2 * r + hs)

        if nn % 2 == 0:  # nn is even.
            y = oy - ( (r + vs / 2) + (nn // 2) * (2 * r + vs) )
        else:  # nn is odd.
            y = oy - ((nn // 2 + 1) * (2 * r + vs))

        for k in range(nn):
            y = y + (2 * r + (vs / 2))
            node = add_node(net, "%s%s"%(l, k), x, y)
            neurons[l].append(node)

        add_edges(net, neurons, l)

    return net


def update(nav, net):
    layers = [3, 6, 9, 9, 6, 3, 1]
    net = create_network(layers)

    dpath = osp.join(osp.dirname(__file__), "neural-networks")
    os.makedirs(dpath, exist_ok=True)
    fpath = osp.join(dpath, "neural-network-n%d.jpg" % (sum(layers)))

    write_image(net, fpath, scale_width=50, scale_height=50, dpi_width=300, dpi_height=300)

    nav.append_item(net)
