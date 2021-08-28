import random
import math

import networkx as nx

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor
from qtpy.QtGui import QFont

import nezzle
from nezzle.graphics import NodeClassFactory
from nezzle.graphics import LinkClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import Network
from nezzle.graphics import SelfloopLink
from nezzle.constants import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT
from nezzle.utils.math import rotate, dist, internal_division


def to_graphics(dg, iden, no_link_type=False):
    if not isinstance(dg, nx.DiGraph):
        raise TypeError("NetworkX.DiGraph should be given, not %s"%(type(dg)))

    net = Network(iden)
    #net.scene.setBackgroundBrush(QColor(0, 0, 0, 0))
    net.scene.setBackgroundBrush(Qt.transparent)

    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
    nodes = {}
    counter_node = 0
    counter_link = 0

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

    # Link types
    str_act = '+'
    str_inh = '-'

    for str_src, str_tgt, link_data in dg.edges(data=True):
        str_link_type = None
        head = None

        if not no_link_type:
            if 'HEAD' in link_data:
                if isinstance(link_data['HEAD'], dict):
                    attr_head = link_data.pop('HEAD')
                    ArrowClass = ArrowClassFactory.create(attr_head['TYPE'])
                    head = ArrowClass.from_dict(attr_head)
                    # if dict_head['TYPE'] == 'TRIANGLE':
                    #     str_link_type = '+'
                    # elif dict_head['TYPE'] == 'HAMMER':
                    #     str_link_type = '-'
                else:
                    str_link_type = link_data.pop('HEAD')
            elif 'SIGN' in link_data:
                sign_link = link_data['SIGN']
                if sign_link > 0:
                    str_link_type = str_act
                elif sign_link < 0:
                    str_link_type = str_inh
                else:
                    raise ValueError("Undefined link sign: %s"%(sign_link))

        if not head and not no_link_type \
           and (str_link_type not in (str_act, str_inh)):
            raise ValueError("Undefined link type: %s"%(str_link_type))

        if 'POS_X' in dg.nodes[str_src]:
            sx = dg.nodes[str_src]['POS_X']
        else:
            sx = half_width + random.uniform(*range_x)

        if 'POS_Y' in dg.nodes[str_src]:
            sy = dg.nodes[str_src]['POS_Y']
        else:
            sy = half_height + random.uniform(*range_y)

        if 'POS_X' in dg.nodes[str_tgt]:
            tx = dg.nodes[str_tgt]['POS_X']
        else:
            tx = half_width + random.uniform(*range_x)

        if 'POS_Y' in dg.nodes[str_tgt]:
            ty = dg.nodes[str_tgt]['POS_Y']
        else:
            ty = half_height + random.uniform(*range_y)

        if str_src in nodes:
            src = nodes[str_src]
        else:
            counter_node += 1
            src = NodeClass(str_src, width=width, height=height,
                            pos=QPointF(sx, sy))

            if 'FILL_COLOR' not in dg.nodes[str_src]:
                src['FILL_COLOR'] = color_node

            if 'BORDER_COLOR' not in dg.nodes[str_src]:
                src['BORDER_COLOR'] = Qt.darkGray

            src.update(dg.nodes[str_src])
            nodes[str_src] = src
        # end of else

        if str_tgt in nodes:
            tgt = nodes[str_tgt]
        else:
            counter_node += 1
            tgt = NodeClass(str_tgt, width=width, height=height,
                            pos=QPointF(tx, ty))

            if 'FILL_COLOR' not in dg.nodes[str_tgt]:
                tgt['FILL_COLOR'] = color_node

            if 'BORDER_COLOR' not in dg.nodes[str_tgt]:
                tgt['BORDER_COLOR'] = Qt.darkGray

            tgt.update(dg.nodes[str_tgt])
            nodes[str_tgt] = tgt
        # end of else

        counter_link += 1

        # Add head
        if not head:  # Head can created according to head information.
            if no_link_type:
                ArrowClass = None
            elif str_link_type == '+':
                head_type = 'TRIANGLE'
                ArrowClass = ArrowClassFactory.create(head_type)
            elif str_link_type == '-':
                head_type = 'HAMMER'
                ArrowClass = ArrowClassFactory.create(head_type)
            else:
                pass  # This logic is processed just below.

            if ArrowClass:
                head = ArrowClass()

        # Add link with head
        if str_src == str_tgt:  # Self-loop link
            LinkClass = LinkClassFactory.create('SELFLOOP_LINK')
            iden = "%s%s%s" % (str_src, str_link_type, str_src)
            link = LinkClass(iden=iden,
                             name=str_link_type,
                             node=src,
                             head=head)

            if 'FILL_COLOR' not in link_data:
                link['FILL_COLOR'] = QColor(100, 100, 100, 100)

            # Update extra data in nezzle.graphics.Link object.
            link.update(link_data)
        else:
            LinkClass = LinkClassFactory.create('CURVED_LINK')
            iden = "%s%s%s" % (str_src, str_link_type, str_tgt)
            link = LinkClass(iden=iden,
                             name= str_link_type,
                             source=src, target=tgt,
                             head=head)

            if 'FILL_COLOR' not in link_data:
                link['FILL_COLOR'] = Qt.black

            # Update extra data in nezzle.graphics.Link object.
            link.update(link_data)
        # end of else

        src.add_link(link)
        tgt.add_link(link)
        net.add_link(link)
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

    # Make the two links of interconnected nodes curved.
    for src, tgt, attr in net.nxdg.edges(data=True):
        if net.nxdg.has_edge(tgt, src):
            if src == tgt:  # Skip selfloops
                continue

            link = attr['VIS']
            mid = internal_division(link.pos_src, link.pos_tgt, 0.5, 0.5)
            d = dist(link.pos_src, mid)/math.cos(math.pi/4)
            cp = rotate(link.pos_src, mid, -30, d)
            link.ctrl_point.setPos(cp)

    return net


def to_networkx(net):
    if not isinstance(net, nezzle.graphics.Network):
        raise TypeError("nezzle.graphics.Network should be given, not %s"%(type(net)))

    dg = nx.DiGraph()
    dg.name = net.iden

    for iden, link in net.links.items():

        if isinstance(link, SelfloopLink):
            src = tgt = link.node
        else:
            src = link.source
            tgt = link.target

        if src.iden not in dg.nodes:
            dg.add_node(src.iden)
            dg.nodes[src.iden].update(src.to_dict())

        if tgt.iden not in dg.nodes:
            dg.add_node(tgt.iden)
            dg.nodes[tgt.iden].update(tgt.to_dict())


        dg.add_edge(src.iden, tgt.iden)
        link_data = dg.edges[src.iden, tgt.iden]
        link_data.update(link.to_dict())

        # Set sign information if head exists.
        if link.head:
            sign_link = 0
            if link.head.TYPE == 'TRIANGLE':
                sign_link = +1
            elif link.head.TYPE == 'HAMMER':
                sign_link = -1

            link_data['SIGN'] = sign_link

    return dg
