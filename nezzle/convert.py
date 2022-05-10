import random
import math

import networkx as nx

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor
from qtpy.QtGui import QFont

import nezzle
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import EdgeClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import Network
from nezzle.graphics import SelfloopEdge
from nezzle.constants import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT
from nezzle.utils.math import rotate, dist, internal_division


def to_graphics(dg, iden, no_edge_type=False):
    if not isinstance(dg, nx.DiGraph):
        raise TypeError("NetworkX.DiGraph should be given, not %s"%(type(dg)))

    net = Network(iden)
    #net.scene.setBackgroundBrush(QColor(0, 0, 0, 0))
    net.scene.setBackgroundBrush(Qt.transparent)

    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
    nodes = {}
    counter_node = 0
    counter_edge = 0

    # Set constants with default values
    scene_width = DEFAULT_SCENE_WIDTH
    scene_height = DEFAULT_SCENE_HEIGHT

    # Node color
    color_node = Qt.white
    half_width = scene_width / 2
    half_height = scene_height / 2

    range_x = (-scene_width / 4, scene_width / 4)
    range_y = (-scene_height / 4, scene_height / 4)

    # Node size
    width = 50
    height = 35

    # Edge types
    str_act = '+'
    str_inh = '-'

    for str_src, str_trg, edge_data in dg.edges(data=True):
        str_edge_type = None
        head = None

        if not no_edge_type:
            if 'HEAD' in edge_data:
                if isinstance(edge_data['HEAD'], dict):
                    attr_head = edge_data.pop('HEAD')
                    ArrowClass = ArrowClassFactory.create(attr_head['ITEM_TYPE'])
                    head = ArrowClass.from_dict(attr_head)
                    # if dict_head['ITEM_TYPE'] == "TRIANGLE":
                    #     str_edge_type = '+'
                    # elif dict_head['ITEM_TYPE'] == "HAMMER":
                    #     str_edge_type = '-'
                else:
                    str_edge_type = edge_data.pop('HEAD')
            elif 'SIGN' in edge_data:
                sign_edge = edge_data['SIGN']
                if sign_edge > 0:
                    str_edge_type = str_act
                elif sign_edge < 0:
                    str_edge_type = str_inh
                else:
                    raise ValueError("Undefined edge sign: %s"%(sign_edge))

        if not head and not no_edge_type \
           and (str_edge_type not in (str_act, str_inh)):
            raise ValueError("Undefined edge type: %s"%(str_edge_type))

        if 'POS_X' in dg.nodes[str_src]:
            sx = dg.nodes[str_src]['POS_X']
        else:
            sx = half_width + random.uniform(*range_x)

        if 'POS_Y' in dg.nodes[str_src]:
            sy = dg.nodes[str_src]['POS_Y']
        else:
            sy = half_height + random.uniform(*range_y)

        if 'POS_X' in dg.nodes[str_trg]:
            tx = dg.nodes[str_trg]['POS_X']
        else:
            tx = half_width + random.uniform(*range_x)

        if 'POS_Y' in dg.nodes[str_trg]:
            ty = dg.nodes[str_trg]['POS_Y']
        else:
            ty = half_height + random.uniform(*range_y)

        if str_src in nodes:
            src = nodes[str_src]
        else:
            counter_node += 1
            src = NodeClass(str_src, width=width, height=height,
                            pos=QPointF(sx, sy))

            if "FILL_COLOR" not in dg.nodes[str_src]:
                src["FILL_COLOR"] = color_node

            if 'BORDER_COLOR' not in dg.nodes[str_src]:
                src['BORDER_COLOR'] = Qt.darkGray

            src.update(dg.nodes[str_src])
            nodes[str_src] = src
        # end of else

        if str_trg in nodes:
            trg = nodes[str_trg]
        else:
            counter_node += 1
            trg = NodeClass(str_trg, width=width, height=height,
                            pos=QPointF(tx, ty))

            if "FILL_COLOR" not in dg.nodes[str_trg]:
                trg["FILL_COLOR"] = color_node

            if 'BORDER_COLOR' not in dg.nodes[str_trg]:
                trg['BORDER_COLOR'] = Qt.darkGray

            trg.update(dg.nodes[str_trg])
            nodes[str_trg] = trg
        # end of else

        counter_edge += 1

        # Add head
        if not head:  # Head can created according to head information.
            if no_edge_type:
                ArrowClass = None
            elif str_edge_type == '+':
                head_type = "TRIANGLE"
                ArrowClass = ArrowClassFactory.create(head_type)
            elif str_edge_type == '-':
                head_type = "HAMMER"
                ArrowClass = ArrowClassFactory.create(head_type)
            else:
                pass  # This logic is processed just below.

            if ArrowClass:
                head = ArrowClass()

        # Add edge with head
        if str_src == str_tgt:  # Self-loop edge
            EdgeClass = EdgeClassFactory.create('SELFLOOP_EDGE')
            iden = "%s%s%s" % (str_src, str_edge_type, str_src)
            edge = EdgeClass(iden=iden,
                             name=str_edge_type,
                             node=src,
                             head=head)

            if "FILL_COLOR" not in edge_data:
                edge["FILL_COLOR"] = QColor(100, 100, 100, 100)

            # Update extra data in nezzle.graphics.Edge object.
            edge.update(edge_data)
        else:
            EdgeClass = EdgeClassFactory.create('CURVED_EDGE')
            iden = "%s%s%s" % (str_src, str_edge_type, str_tgt)
            edge = EdgeClass(iden=iden,
                             name= str_edge_type,
                             source=src, target=trg,
                             head=head)

            if "FILL_COLOR" not in edge_data:
                edge["FILL_COLOR"] = Qt.black

            # Update extra data in nezzle.graphics.Edge object.
            edge.update(edge_data)
        # end of else

        src.add_edge(edge)
        trg.add_edge(edge)
        net.add_edge(edge)
    # end of for : reading each line of SIF file

    # Add nodes and labels in network
    font = QFont()
    font.setFamily("Tahoma")
    font.setPointSize(10)
    LabelClass = LabelClassFactory.create("TEXT_LABEL")
    for str_name, node in nodes.items():
        net.add_node(node)
        label = LabelClass(node, str_name)
        label.font = font
        rect = label.boundingRect()
        label.setPos(-rect.width()/2, -rect.height()/2)
        net.add_label(label)
        nodes[str_name] = node

    # Make the two edges of interconnected nodes curved.
    for src, trg, attr in net.nxgraph.edges(data=True):
        if net.nxgraph.has_edge(trg, src):
            if src == trg:  # Skip selfloops
                continue

            edge = attr['GRAPHICS']
            mid = internal_division(edge.pos_src, edge.pos_tgt, 0.5, 0.5)
            d = dist(edge.pos_src, mid)/math.cos(math.pi/4)
            cp = rotate(edge.pos_src, mid, -30, d)
            edge.ctrl_point.setPos(cp)

    return net


def to_networkx(net):
    if not isinstance(net, nezzle.graphics.Network):
        raise TypeError("nezzle.graphics.Network should be given, not %s"%(type(net)))

    dg = nx.DiGraph()
    dg.name = net.iden

    for iden, edge in net.edges.items():

        if isinstance(edge, SelfloopEdge):
            src = trg = edge.node
        else:
            src = edge.source
            trg = edge.target

        if src.iden not in dg.nodes:
            dg.add_node(src.iden)
            dg.nodes[src.iden].update(src.to_dict())

        if trg.iden not in dg.nodes:
            dg.add_node(trg.iden)
            dg.nodes[trg.iden].update(trg.to_dict())


        dg.add_edge(src.iden, trg.iden)
        edge_data = dg.edges[src.iden, trg.iden]
        edge_data.update(edge.to_dict())

        # Set sign information if head exists.
        if edge.head:
            sign_edge = 0
            if edge.head.ITEM_TYPE == "TRIANGLE":
                sign_edge = +1
            elif edge.head.ITEM_TYPE == "HAMMER":
                sign_edge = -1

            edge_data['SIGN'] = sign_edge

    return dg
