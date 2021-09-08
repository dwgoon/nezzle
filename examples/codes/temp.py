from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF

from nezzle.managers import NavigationTreeManager
from nezzle.graphics import EllipseNode
from nezzle.graphics import Network


def update(nav, net):
    """update() is called by Nezzle to update the items of the navigation.

    Args:
        nav (NavigationTreeManager): the navigation , which adds network items.
        net (Network): the currently selected network item.
    """

    net = Network("A single node")

    node = EllipseNode('SRC1', 40, 40, pos=QPointF(0, 0))
    node['FILL_COLOR'] = Qt.yellow
    node["BORDER_COLOR"] = Qt.black
    node['BORDER_WIDTH'] = 2
    net.add_node(node)

    nav.append_item(net)
