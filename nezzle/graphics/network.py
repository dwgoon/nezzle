# -*- coding: utf-8 -*-

import math
import random

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor
from qtpy.QtGui import QFont

import networkx as nx

from .nodes.nodefactory import NodeClassFactory
from .links.linkfactory import LinkClassFactory
from .labels.labelfactory import LabelClassFactory
from .header import HeaderClassFactory

from .links.baselink import BaseLink
from .labels.textlabel import TextLabel
from .nodes.basenode import BaseNode

from nezzle.graphics import SelfloopLink
from nezzle.graphics.baseitem import MappableItem
from nezzle.graphics.screen import GraphicsScene
from nezzle.utils.math import rotate, dist, internal_division


class Network(MappableItem):
    def __init__(self, iden, name=None):
        self._item = None
        super().__init__(iden, name=name)
        self._nodes = {}
        self._links = {}
        self._labels = {}
        self._scene = GraphicsScene()
        self._nxdg = nx.DiGraph(name=name)
        self.nxdg.labels = {}

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
    def links(self):
        return self._links

    @property
    def labels(self):
        return self._labels

    @property
    def scene(self):
        return self._scene

    @property
    def nxdg(self):
        return self._nxdg

    def _trigger_set_name(self, key, value):
        self._name = value
        if self._item:
            self._item.setText(self._name)

        return value

    def add_node(self, node):
        self.nodes[node.iden] = node
        self.scene.addItem(node)
        self.nxdg.add_node(node.iden)
        self.nxdg.nodes[node.iden]['VIS'] = node

    def remove_node(self, obj):
        if isinstance(obj, BaseNode):
            iden = obj.iden
        elif isinstance(obj, str):
            iden = obj

        node = self.nodes[iden]
        while node.links:
            link = node.links.pop()
            self.remove_link(link)

        self.scene.removeItem(node)
        del self.nodes[iden]

    def add_link(self, link):
        """Add a links object.

        Parameters
        ----------
        link : nezzle.graphics.BaseLink
            Link object derived from nezzle.graphics.BaseLink.

        Returns
        -------
        None

        """
        self.links[link.iden] = link
        self.scene.addItem(link)

        if isinstance(link, SelfloopLink):
            iden_src = iden_tgt = link.node.iden
        else:
            iden_src = link.source.iden
            iden_tgt = link.target.iden

        self.nxdg.add_edge(iden_src, iden_tgt)
        self.nxdg[iden_src][iden_tgt]['VIS'] = link

    def remove_link(self, obj):
        if isinstance(obj, BaseLink):
            iden = obj.iden
        elif isinstance(obj, str):
            iden = obj

        link = self.links[iden]
        self.scene.removeItem(link)
        if isinstance(obj, SelfloopLink):
            self.nxdg.remove_edge(link.node.iden, link.node.iden)
            link.node.remove_link(link)
        else:
            self.nxdg.remove_edge(link.source.iden, link.target.iden)
            link.source.remove_link(link)
            link.target.remove_link(link)

        del self.links[iden]

    def add_label(self, label):
        self.labels[label.iden] = label
        self.nxdg.labels[label.iden] = {}
        self.nxdg.labels[label.iden]['VIS'] = label

    def remove_label(self, obj):
        if isinstance(obj, TextLabel):
            iden = obj.iden
        elif isinstance(obj, str):
            iden = obj

        self.scene.removeItem(self.labels[iden])
        del self.labels[iden]

    def copy(self):
        # obj = self.__class__()
        # obj.name = self.name
        # obj._scene.setSceneRect(0, 0, self.scene.width(), self.scene.height())
        # obj._scene.setBackgroundBrush(self.scene.backgroundBrush())
        #
        # for iden, nodes in self.nodes.items():
        #     obj.add_node(nodes.copy())
        # for iden, links in self.links.items():
        #     obj.add_link(links.copy())
        # for iden, labels in self.labels.items():
        #     obj.add_label(labels.copy())
        #
        # return obj
        return self.from_dict(self.to_dict())

    def to_dict(self):
        dict_net = {}

        dict_net["NEZZLE_VERSION"] = (0, 0, 1)
        dict_net["NAME"] = self.name

        bg_color = self.scene.backgroundBrush().color()
        dict_net["BACKGROUND_COLOR"] = bg_color.name(QColor.HexArgb)

        dict_net["NODES"] = []
        dict_net["LINKS"] = []
        dict_net["LABELS"] = []

        for iden, node in self.nodes.items():
            dict_net["NODES"].append(node.to_dict())

        for iden, link in self.links.items():
            dict_net["LINKS"].append(link.to_dict())

        for iden, label in self.labels.items():
            dict_net["LABELS"].append(label.to_dict())

        dict_net.update(self._attr)
        return dict_net

    @classmethod
    def from_dict(cls, dict_net):
        """
        Adding objects should be in the following order:

            Link -> Node -> Label

        This order prevents an abnormal visualization.
        """
        # TODO: Using Z-value for maintaining the order.

        net = cls(dict_net['ID'])
        net.name = dict_net['NAME']

        #scene_width = dict_net["SCENE"]["SCENE_WIDTH"]
        #scene_height = dict_net["SCENE"]["SCENE_HEIGHT"]
        #net.scene.setSceneRect(0, 0, scene_width, scene_height)

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

        for dict_link in dict_net["LINKS"]:
            item_type = dict_link.pop("ITEM_TYPE")

            if 'SELFLOOP' in item_type:
                iden_node = dict_link.pop("ID_NODE")
                node = dict_graphics[iden_node]
                LinkClass = LinkClassFactory.create(item_type)
                link = LinkClass.from_dict(dict_link, node)
            else:
                iden_src = dict_link.pop("ID_SOURCE")
                iden_tgt = dict_link.pop("ID_TARGET")
                src = dict_graphics[iden_src]
                tgt = dict_graphics[iden_tgt]
                LinkClass = LinkClassFactory.create(item_type)
                link = LinkClass.from_dict(dict_link, src, tgt)

            dict_graphics[link.iden] = link
            net.add_link(link)
            link.update()

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


def from_adj_to_net(A, i2n, name='network', msc=None, nodes=None):
    """Create a network using adjacency matrix.

    Parameters
    ----------
    A : numpy.ndarray
        Adjacency matrix.
    i2n : dict
        Dictionary for mapping index to name.
        Node IDs and labels are created from this dictionary.
    name : str, optional
        Network name, also used for network identity.
    msc : dict, optional
        Dictionary for mapping signs to links classes.
        If it is not given, a positive value in the adjacency
        is used for creating arrow links, and a negative value
        for creating hammer links.
    nodes : dict, optional
        Dictionary of nodes objects (nezzle.graphics.BaseNode).
        The new nodes are created by copying these nodes.
        This dictionary should be given with i2n.


    Returns
    -------
    net : nezzle.graphics.Network
        Network object.
    """

    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
    LinkClass = LinkClassFactory.create("CURVED_LINK")
    SelfloopClass = LinkClassFactory.create("SELFLOOP_LINK")
    LabelClass = LabelClassFactory.create("TEXT_LABEL")

    if not nodes:
        nodes = {}
        range_pos = (0, 500)
        width = 50
        height = 35
        for iden in i2n.values():
            x = random.uniform(*range_pos)
            y = random.uniform(*range_pos)
            node = NodeClass(iden, pos=QPointF(x, y),
                                    width=width, height=height)

            node['BORDER_COLOR'] = Qt.darkGray

            nodes[iden] = node

    if not msc:
        msc = {}
        msc['+'] = HeaderClassFactory.create('ARROW')
        msc['-'] = HeaderClassFactory.create('HAMMER')


    ir, ic = A.nonzero()
    nodes_cache = {}
    net_new = Network(name)
    # net_new.scene.setBackgroundBrush(QColor(0, 0, 0, 0))
    net_new.scene.setBackgroundBrush(Qt.transparent)
    for i in range(ir.size):
        itgt, isrc = ir[i], ic[i]
        tgt, src = i2n[itgt], i2n[isrc]

        sign = '+' if A[itgt, isrc] > 0 else '-'
        HeaderClass = msc[sign]
        header = HeaderClass()

        iden = "%s%s%s" % (src, sign, tgt)

        if src == tgt:
            if src not in nodes_cache:
                node = nodes[src].copy()
                nodes_cache[src] = node
            else:
                node = nodes_cache[src]

            link = SelfloopClass(iden=iden,
                                 node=node,
                                 header=header)

            node.add_link(link)
            net_new.add_link(link)
        else:  # Two-nodes links
            if src not in nodes_cache:
                node_src = nodes[src].copy()
                nodes_cache[src] = node_src
            else:
                node_src = nodes_cache[src]

            if tgt not in nodes_cache:
                node_tgt = nodes[tgt].copy()
                nodes_cache[tgt] = node_tgt
            else:
                node_tgt = nodes_cache[tgt]

            link = LinkClass(iden=iden,
                             source=node_src,
                             target=node_tgt,
                             header=header)

            node_src.add_link(link)
            node_tgt.add_link(link)
            net_new.add_link(link)

            # end of for

    # Add labels
    font = QFont()
    font.setFamily("Tahoma")
    font.setPointSize(10)

    for str_name, node in nodes_cache.items():
        net_new.add_node(node)
        label = LabelClass(node, str_name)
        label.font = font
        rect = label.boundingRect()
        label.setPos(-rect.width() / 2, -rect.height() / 2)
        net_new.add_label(label)

    for src, tgt, attr in net_new.nxdg.edges(data=True):
        if net_new.nxdg.has_edge(tgt, src):
            if src == tgt:  # Skip selfloops
                continue

            link = attr['VIS']
            mid = internal_division(link.pos_src, link.pos_tgt, 0.5, 0.5)
            d = dist(link.pos_src, mid) / math.cos(math.pi / 4)
            cp = rotate(link.pos_src, mid, -30, d)
            link.ctrl_point.setPos(cp)

    return net_new