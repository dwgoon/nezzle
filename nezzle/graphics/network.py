import math
import random

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor
from qtpy.QtGui import QFont

import networkx as nx

import nezzle

from nezzle.graphics.nodes.nodefactory import NodeClassFactory
from nezzle.graphics.edges.edgefactory import EdgeClassFactory
from nezzle.graphics.labels.labelfactory import LabelClassFactory
from nezzle.graphics.arrows.arrowclassfactory import ArrowClassFactory

from nezzle.graphics.edges.baseedge import BaseEdge
from nezzle.graphics.labels.textlabel import TextLabel
from nezzle.graphics.nodes.basenode import BaseNode

from nezzle.graphics import SelfloopEdge
from nezzle.graphics.baseitem import MappableItem
from nezzle.graphics.screen import GraphicsScene
from nezzle.utils.math import rotate, dist, internal_division


class Network(MappableItem):
    def __init__(self, iden, name=None):
        self._item = None
        super().__init__(iden, name=name)
        self._nodes = {}
        self._edges = {}
        self._labels = {}
        self._scene = GraphicsScene()
        self._nxgraph = nx.DiGraph(name=name)
        self.nxgraph.labels = {}

        self._attr.set_trigger('BACKGROUND_COLOR', self._trigger_set_background_color)


    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s (%s) object at %s' % (__class__, self.name, id(self))

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, obj):
        self._item = obj

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    @property
    def labels(self):
        return self._labels

    @property
    def scene(self):
        return self._scene

    @property
    def nxgraph(self):
        return self._nxgraph

    def _trigger_set_name(self, key, value):
        self._name = value
        if self._item:
            self._item.setText(self._name)

        return value

    def _trigger_set_background_color(self, key, value):
        self._background_color = QColor(value)
        self.scene.setBackgroundBrush(self._background_color)
        return self._background_color.name(QColor.HexArgb)

    def add_node(self, node):
        node.setZValue(0)
        self.nodes[node.iden] = node
        self.scene.addItem(node)
        self.nxgraph.add_node(node.iden)
        self.nxgraph.nodes[node.iden]['GRAPHICS'] = node

    def remove_node(self, obj):
        if isinstance(obj, BaseNode):
            iden = obj.iden
        elif isinstance(obj, str):
            iden = obj

        node = self.nodes[iden]
        while node.edges:
            edge = node.edges.pop()
            self.remove_edge(edge)

        self.scene.removeItem(node)
        del self.nodes[iden]

    def replace_node(self, old_node, new_node):
        while old_node.edges:
            edge = old_node.edges.pop()  # Remove all edges from old node

            if isinstance(edge, SelfloopEdge):
                edge.node = new_node
                new_node.add_edge(edge)
                continue

            if id(edge.source) == id(old_node):
                edge.source = new_node
                new_node.add_edge(edge)
            elif id(edge.target) == id(old_node):
                edge.target = new_node
                new_node.add_edge(edge)
            else:
                raise RuntimeError("[SYSTEM] this point should not be reached!")
        # end of while

        # Add the new node.
        self.add_node(new_node)

        # Re-organize children.
        for child in old_node.childItems():
            child.setParentItem(new_node)

        # Remove the old node from the scene.
        self.scene.removeItem(old_node)

    def replace_edge(self, old_edge, new_edge):

        if isinstance(old_edge, SelfloopEdge):
            self.nxgraph.remove_edge(old_edge.node.iden, old_edge.node.iden)
            self.nxgraph.add_edge(new_edge.node.iden, new_edge.node.iden)

            old_edge.node.remove_edge(old_edge)
            old_edge.node.add_edge(new_edge)
        else:
            self.nxgraph.remove_edge(old_edge.source.iden, old_edge.target.iden)
            self.nxgraph.add_edge(new_edge.source.iden, new_edge.target.iden)

            old_edge.source.remove_edge(old_edge)
            old_edge.target.remove_edge(old_edge)

            old_edge.source.add_edge(new_edge)
            old_edge.target.add_edge(new_edge)

        del self.edges[old_edge.iden]
        self.edges[new_edge.iden] = new_edge

        old_edge.setZValue(-1)
        new_edge.setZValue(-1)
        self.scene.removeItem(old_edge)
        self.scene.addItem(new_edge)
        new_edge.update()

    def add_edge(self, edge):
        """Add a edges object.

        Args:
            edge : nezzle.graphics.BaseEdge
                Edge object derived from nezzle.graphics.BaseEdge.

        Returns:
            None
        """

        edge.setZValue(-1)
        self.edges[edge.iden] = edge
        self.scene.addItem(edge)

        if isinstance(edge, SelfloopEdge):
            iden_src = iden_trg = edge.node.iden
        else:
            iden_src = edge.source.iden
            iden_trg = edge.target.iden

        self.nxgraph.add_edge(iden_src, iden_trg)
        self.nxgraph[iden_src][iden_trg]['GRAPHICS'] = edge

    def remove_edge(self, obj):
        if isinstance(obj, BaseEdge):
            iden = obj.iden
        elif isinstance(obj, str):
            iden = obj

        edge = self.edges[iden]
        self.scene.removeItem(edge)
        if isinstance(obj, SelfloopEdge):
            self.nxgraph.remove_edge(edge.node.iden, edge.node.iden)
            edge.node.remove_edge(edge)
        else:
            self.nxgraph.remove_edge(edge.source.iden, edge.target.iden)
            edge.source.remove_edge(edge)
            edge.target.remove_edge(edge)

        del self.edges[iden]

    def add_label(self, label):
        self.labels[label.iden] = label
        self.nxgraph.labels[label.iden] = {}
        self.nxgraph.labels[label.iden]['GRAPHICS'] = label

    def remove_label(self, obj):
        if isinstance(obj, TextLabel):
            iden = obj.iden
        elif isinstance(obj, str):
            iden = obj

        self.scene.removeItem(self.labels[iden])
        del self.labels[iden]

    def copy(self):
        return self.from_dict(self.to_dict())

    def to_dict(self):
        dict_net = {}

        # TODO: Use a global variable for setting the version
        dict_net["NEZZLE_VERSION"] = tuple(nezzle.__version__.split('.'))
        dict_net["NAME"] = self.name

        bg_color = self.scene.backgroundBrush().color()
        dict_net["BACKGROUND_COLOR"] = bg_color.name(QColor.HexArgb)

        dict_net["NODES"] = []
        dict_net["EDGES"] = []
        dict_net["LABELS"] = []

        for iden, node in self.nodes.items():
            dict_node = node.to_dict()
            dict_node = {key: val for key, val in dict_node.items() if not key.startswith("_")}
            dict_net["NODES"].append(dict_node)

        for iden, edge in self.edges.items():
            dict_edge = edge.to_dict()
            dict_edge = {key: val for key, val in dict_edge.items() if not key.startswith("_")}
            dict_net["EDGES"].append(dict_edge)

        for iden, label in self.labels.items():
            dict_label = label.to_dict()
            dict_label = {key: val for key, val in dict_label.items() if not key.startswith("_")}
            dict_net["LABELS"].append(dict_label)

        dict_net.update(self._attr)
        return dict_net

    @classmethod
    def from_dict(cls, dict_net):
        """
        Adding objects should be in the following order:

            Edge -> Node -> Label

        This order prevents an abnormal visualization.
        """
        # TODO: Using Z-value for maintaining the order.

        net = cls(dict_net['ID'])
        net.name = dict_net['NAME']

        bg_color_rgb = dict_net["BACKGROUND_COLOR"]
        bg_color = QColor(bg_color_rgb)
        net.scene.setBackgroundBrush(bg_color)

        list_nodes = []
        dict_graphics = {}

        for dict_node in dict_net["NODES"]:
            item_type = dict_node.pop('ITEM_TYPE')
            NodeClass = NodeClassFactory.create(item_type)
            node = NodeClass.from_dict(dict_node)
            dict_graphics[node.iden] = node
            list_nodes.append(node)

        for dict_edge in dict_net["EDGES"]:
            item_type = dict_edge.pop("ITEM_TYPE")
            if 'SELFLOOP' in item_type:
                iden_node = dict_edge.pop("ID_NODE")
                node = dict_graphics[iden_node]
                EdgeClass = EdgeClassFactory.create(item_type)
                edge = EdgeClass.from_dict(dict_edge, node)
            else:
                iden_src = dict_edge.pop("ID_SOURCE")
                iden_tgt = dict_edge.pop("ID_TARGET")
                src = dict_graphics[iden_src]
                trg = dict_graphics[iden_tgt]
                EdgeClass = EdgeClassFactory.create(item_type)
                edge = EdgeClass.from_dict(dict_edge, src, trg)

            dict_graphics[edge.iden] = edge
            net.add_edge(edge)
            edge.update()

        for dict_label in dict_net["LABELS"]:
            item_type = dict_label.pop("ITEM_TYPE")
            iden_parent = dict_label.pop("ID_PARENT")
            parent = dict_graphics[iden_parent]
            LabelClass = LabelClassFactory.create(item_type)
            label = LabelClass.from_dict(dict_label, parent)
            net.add_label(label)

        for node in list_nodes:
            net.add_node(node)

        return net
# end of class Network

#
# def from_adj_to_net(A, i2n, name='network', msc=None, nodes=None):
#     """Create a network using adjacency matrix.
#
#     Parameters
#     ----------
#     A : numpy.ndarray
#         Adjacency matrix.
#     i2n : dict
#         Dictionary for mapping index to name.
#         Node IDs and labels are created from this dictionary.
#     name : str, optional
#         Network name, also used for network identity.
#     msc : dict, optional
#         Dictionary for mapping signs to edges classes.
#         If it is not given, a positive value in the adjacency
#         is used for creating arrow edges, and a negative value
#         for creating hammer edges.
#     nodes : dict, optional
#         Dictionary of nodes objects (nezzle.graphics.BaseNode).
#         The new nodes are created by copying these nodes.
#         This dictionary should be given with i2n.
#
#
#     Returns
#     -------
#     net : nezzle.graphics.Network
#         Network object.
#     """
#
#     NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
#     EdgeClass = EdgeClassFactory.create("CURVED_EDGE")
#     SelfloopClass = EdgeClassFactory.create("SELFLOOP_EDGE")
#     LabelClass = LabelClassFactory.create("TEXT_LABEL")
#
#     if not nodes:
#         nodes = {}
#         range_pos = (0, 500)
#         width = 50
#         height = 35
#         for iden in i2n.values():
#             x = random.uniform(*range_pos)
#             y = random.uniform(*range_pos)
#             node = NodeClass(iden, pos=QPointF(x, y),
#                                     width=width, height=height)
#
#             node['BORDER_COLOR'] = Qt.darkGray
#
#             nodes[iden] = node
#
#     if not msc:
#         msc = {}
#         msc['+'] = ArrowClassFactory.create("TRIANGLE")
#         msc['-'] = ArrowClassFactory.create("HAMMER")
#
#
#     ir, ic = A.nonzero()
#     nodes_cache = {}
#     net_new = Network(name)
#     # net_new.scene.setBackgroundBrush(QColor(0, 0, 0, 0))
#     net_new.scene.setBackgroundBrush(Qt.white) #transparent)
#     for i in range(ir.size):
#         itgt, isrc = ir[i], ic[i]
#         trg, src = i2n[itgt], i2n[isrc]
#
#         sign = '+' if A[itgt, isrc] > 0 else '-'
#         ArrowClass = msc[sign]
#         head = ArrowClass()
#
#         iden = "%s%s%s" % (src, sign, trg)
#
#         if src == trg:
#             if src not in nodes_cache:
#                 node = nodes[src].copy()
#                 nodes_cache[src] = node
#             else:
#                 node = nodes_cache[src]
#
#             edge = SelfloopClass(iden=iden,
#                                  node=node,
#                                  head=head)
#
#             node.add_edge(edge)
#             net_new.add_edge(edge)
#         else:  # Two-nodes edges
#             if src not in nodes_cache:
#                 node_src = nodes[src].copy()
#                 nodes_cache[src] = node_src
#             else:
#                 node_src = nodes_cache[src]
#
#             if trg not in nodes_cache:
#                 node_tgt = nodes[trg].copy()
#                 nodes_cache[trg] = node_tgt
#             else:
#                 node_tgt = nodes_cache[trg]
#
#             edge = EdgeClass(iden=iden,
#                              source=node_src,
#                              target=node_tgt,
#                              head=head)
#
#             node_src.add_edge(edge)
#             node_tgt.add_edge(edge)
#             net_new.add_edge(edge)
#
#             # end of for
#
#     # Add labels
#     font = QFont()
#     font.setFamily("Tahoma")
#     font.setPointSize(10)
#
#     for str_name, node in nodes_cache.items():
#         net_new.add_node(node)
#         label = LabelClass(node, str_name)
#         label.font = font
#         rect = label.boundingRect()
#         label.setPos(-rect.width() / 2, -rect.height() / 2)
#         net_new.add_label(label)
#
#     for src, trg, attr in net_new.nxgraph.edges(data=True):
#         if net_new.nxgraph.has_edge(trg, src):
#             if src == trg:  # Skip selfloops
#                 continue
#
#             edge = attr['GRAPHICS']
#             mid = internal_division(edge.pos_src, edge.pos_tgt, 0.5, 0.5)
#             d = dist(edge.pos_src, mid) / math.cos(math.pi / 4)
#             cp = rotate(edge.pos_src, mid, -30, d)
#             edge.ctrl_point.setPos(cp)
#
#     return net_new