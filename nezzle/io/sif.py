import os
import codecs
from collections import defaultdict
import math
import random

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import NodeClassFactory
from nezzle.graphics import EdgeClassFactory
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
            str_src, str_edge_type, str_trg = items[:3]
            interactions[str_edge_type.strip()] += 1

    metadata["NETWORK_NAME"] = os.path.basename(fpath)
    metadata["INTERACTIONS"] = interactions
    return metadata
# end of def


def read_sif(fpath, edge_map=None):

    scene_width = DEFAULT_SCENE_WIDTH
    scene_height = DEFAULT_SCENE_HEIGHT

    fname = os.path.basename(fpath)
    net = Network(fname)
    net.scene.setBackgroundBrush(Qt.transparent)

    with codecs.open(fpath, "r", encoding="utf-8-sig") as fin:
        NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
        nodes = {}
        counter_node = 0
        counter_edge = 0
        for i, line in enumerate(fin):
            if line.isspace():
                continue

            items = line.split()
            str_src, str_edge_type, str_trg = items[:3]

            if edge_map and (str_edge_type not in edge_map):
                raise ValueError("Undefined edge type: %s"%(str_edge_type))

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

            if str_trg in nodes:
                trg = nodes[str_trg]
            else:
                counter_node += 1
                trg = NodeClass(str_trg, width=width, height=height,
                                pos=QPointF(tx, ty))

                trg["FILL_COLOR"] = color
                trg['BORDER_COLOR'] = Qt.darkGray
                nodes[str_trg] = trg
            # end of else

            counter_edge += 1

            head = None
            ArrowClass = None

            if edge_map:
                head_type = edge_map[str_edge_type]
                ArrowClass = ArrowClassFactory.create(head_type)

            if ArrowClass:
                head = ArrowClass()

            if str_src == str_trg: # Self-loop edge
                EdgeClass = EdgeClassFactory.create('SELFLOOP_EDGE')
                iden = "%s%s%s" % (str_src, str_edge_type, str_src)
                edge = EdgeClass(iden=iden,
                                 name=str_edge_type,
                                 node=src,
                                 head=head)

                edge["FILL_COLOR"] = QColor(100, 100, 100, 100)

            else:
                EdgeClass = EdgeClassFactory.create('CURVED_EDGE')
                iden = "%s%s%s" % (str_src, str_edge_type, str_trg)
                edge = EdgeClass(iden=iden,
                                 name= str_edge_type,
                                 source=src, target=trg,
                                 head=head)

                edge["FILL_COLOR"] = Qt.black

            src.add_edge(edge)
            trg.add_edge(edge)
            net.add_edge(edge)
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

    for src, trg, attr in net.nxgraph.edges(data=True):
        if net.nxgraph.has_edge(trg, src):
            if src == trg:  # Skip selfloops
                continue

            edge = attr['GRAPHICS']
            mid = internal_division(edge.pos_src, edge.pos_trg, 0.5, 0.5)
            d = dist(edge.pos_src, mid)/math.cos(math.pi/4)
            cp = rotate(edge.pos_src, mid, -30, d)
            edge.ctrl_point.setPos(cp)

    return net
# end of def


def write_sif(net, fpath):
    with codecs.open(fpath, "w", encoding="utf-8") as fout:
        for iden, edge in net.edges.items():
            if 'SELFLOOP' in edge.ITEM_TYPE:
                args = (edge.node.iden, edge.name, edge.node.iden)
            else:
                args = (edge.source.iden, edge.name, edge.target.iden)
            fout.write("%s\t%s\t%s\n"%args)
# end of def
