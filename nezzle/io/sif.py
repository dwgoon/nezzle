import os
import codecs
from collections import defaultdict
import math
import random

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import NodeClassFactory
from nezzle.graphics import LinkClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import Network
from nezzle.utils.math import rotate, dist, internal_division
from nezzle.constants import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT


def read_metadata_from_sif(fpath):
    metadata = {}
    interactions = defaultdict(int)
    with codecs.open(fpath, "r", encoding="utf-8-sig") as fin:
        for i, line in enumerate(fin):
            if line.isspace():
                continue

            items = line.split()
            str_src, str_link_type, str_tgt = items[:3]
            interactions[str_link_type.strip()] += 1

    metadata["NETWORK_NAME"] = os.path.basename(fpath)
    metadata["INTERACTIONS"] = interactions
    return metadata
# end of def


def read_sif(fpath, link_map=None):

    scene_width = DEFAULT_SCENE_WIDTH
    scene_height = DEFAULT_SCENE_HEIGHT

    fname = os.path.basename(fpath)
    net = Network(fname)
    net.scene.setBackgroundBrush(Qt.transparent)

    with codecs.open(fpath, "r", encoding="utf-8-sig") as fin:
        NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
        nodes = {}
        counter_node = 0
        counter_link = 0
        for i, line in enumerate(fin):
            if line.isspace():
                continue

            items = line.split()
            str_src, str_link_type, str_tgt = items[:3]

            if link_map and (str_link_type not in link_map):
                raise ValueError("Undefined link type: %s"%(str_link_type))

            color = Qt.white
            half_width = scene_width/2
            half_height = scene_height/2

            range_x = (-scene_width/4, scene_width/4)
            range_y = (-scene_height/4, scene_height/4)

            sx = half_width + random.uniform(*range_x)
            sy = half_height + random.uniform(*range_y)

            tx = half_width + random.uniform(*range_x)
            ty = half_height + random.uniform(*range_y)

            width = 50
            height = 35

            if str_src in nodes:
                src = nodes[str_src]
            else:
                counter_node += 1
                src = NodeClass(str_src, width=width, height=height,
                                pos=QPointF(sx, sy))

                src["FILL_COLOR"] = color
                src['BORDER_COLOR'] = Qt.darkGray
                nodes[str_src] = src
            # end of else

            if str_tgt in nodes:
                tgt = nodes[str_tgt]
            else:
                counter_node += 1
                tgt = NodeClass(str_tgt, width=width, height=height,
                                pos=QPointF(tx, ty))

                tgt["FILL_COLOR"] = color
                tgt['BORDER_COLOR'] = Qt.darkGray
                nodes[str_tgt] = tgt
            # end of else

            counter_link += 1

            head = None
            ArrowClass = None

            if link_map:
                head_type = link_map[str_link_type]
                ArrowClass = ArrowClassFactory.create(head_type)

            if ArrowClass:
                head = ArrowClass()

            if str_src == str_tgt: # Self-loop link
                LinkClass = LinkClassFactory.create('SELFLOOP_LINK')
                iden = "%s%s%s" % (str_src, str_link_type, str_src)
                link = LinkClass(iden=iden,
                                 name=str_link_type,
                                 node=src,
                                 head=head)

                link["FILL_COLOR"] = QColor(100, 100, 100, 100)

            else:
                LinkClass = LinkClassFactory.create('CURVED_LINK')
                iden = "%s%s%s" % (str_src, str_link_type, str_tgt)
                link = LinkClass(iden=iden,
                                 name= str_link_type,
                                 source=src, target=tgt,
                                 head=head)

                link["FILL_COLOR"] = Qt.black

            src.add_link(link)
            tgt.add_link(link)
            net.add_link(link)
        # end of for: reading each line of SIF file

        # Add nodes and labels in network
        LabelClass = LabelClassFactory.create("TEXT_LABEL")
        for str_name, node in nodes.items():
            net.add_node(node)
            label = LabelClass(node, str_name)
            label["FONT_FAMILY"] = "Tahoma"
            label["FONT_SIZE"] = 10
            rect = label.boundingRect()
            label.setPos(-rect.width()/2, -rect.height()/2)
            net.add_label(label)
            nodes[str_name] = node
    # end of with

    for src, tgt, attr in net.nxdg.edges(data=True):
        if net.nxdg.has_edge(tgt, src):
            if src == tgt:  # Skip selfloops
                continue

            link = attr['GRAPHICS']
            mid = internal_division(link.pos_src, link.pos_tgt, 0.5, 0.5)
            d = dist(link.pos_src, mid)/math.cos(math.pi/4)
            cp = rotate(link.pos_src, mid, -30, d)
            link.ctrl_point.setPos(cp)

    return net
# end of def


def write_sif(net, fpath):
    with codecs.open(fpath, "w", encoding="utf-8") as fout:
        for iden, link in net.links.items():
            if 'SELFLOOP' in link.ITEM_TYPE:
                args = (link.node.iden, link.name, link.node.iden)
            else:
                args = (link.source.iden, link.name, link.target.iden)
            fout.write("%s\t%s\t%s\n"%args)
# end of def
