import os
import random
import json
import codecs

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor
from qtpy.QtGui import QFont
from qtpy.QtGui import QImage
from qtpy.QtGui import QPainter


from nezzle.graphics import NodeClassFactory
from nezzle.graphics import LinkClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import HeaderClassFactory
from nezzle.graphics import Network
from nezzle.constants import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT
from nezzle.utils import extract_name_and_ext

import math
from nezzle.utils.math import rotate, dist, internal_division


def read_network(fpath, link_map=None):
    if not fpath:
        raise ValueError("Invalid file path: %s"%(fpath))
    file_name_ext = os.path.basename(fpath)
    fname, fext = os.path.splitext(file_name_ext)

    if file_name_ext.endswith('.sif'):
        return read_sif(fpath, link_map)
    elif file_name_ext.endswith('.json'):
        return read_json(fpath)

    else:
        raise ValueError("Unsupported file type: %s"%(fext))
# end of read_network



# TODO: need to make a rule to map str_act and str_inh
def read_sif(fpath, link_map=None):

    scene_width = DEFAULT_SCENE_WIDTH
    scene_height = DEFAULT_SCENE_HEIGHT

    fname = os.path.basename(fpath)
    net = Network(fname)
    net.scene.setBackgroundBrush(QColor(0, 0, 0, 0))

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

                src['FILL_COLOR'] = color
                src['BORDER_COLOR'] = Qt.darkGray
                nodes[str_src] = src
            # end of else

            if str_tgt in nodes:
                tgt = nodes[str_tgt]
            else:
                counter_node += 1
                tgt = NodeClass(str_tgt, width=width, height=height,
                                pos=QPointF(tx, ty))

                tgt['FILL_COLOR'] = color
                tgt['BORDER_COLOR'] = Qt.darkGray
                nodes[str_tgt] = tgt
            # end of else

            counter_link += 1

            header = None
            HeaderClass = None
            """
            if no_link_type:
                HeaderClass = None
            elif str_link_type == '+':
                header_type = 'ARROW'
                HeaderClass = HeaderClassFactory.create(header_type)
            elif str_link_type == '-':
                header_type = 'HAMMER'
                HeaderClass = HeaderClassFactory.create(header_type)
            """
            if link_map:
                header_type = link_map[str_link_type]
                HeaderClass = HeaderClassFactory.create(header_type)

            if HeaderClass:
                header = HeaderClass()

            if str_src == str_tgt: # Self-loop lins
                LinkClass = LinkClassFactory.create('SELFLOOP_LINK')
                iden = "%s%s%s" % (str_src, str_link_type, str_src)
                link = LinkClass(iden=iden,
                                 name=str_link_type,
                                 node=src,
                                 header=header)

                link['FILL_COLOR'] = QColor(100, 100, 100, 100)

            else:
                LinkClass = LinkClassFactory.create('CURVED_LINK')
                iden = "%s%s%s" % (str_src, str_link_type, str_tgt)
                link = LinkClass(iden=iden,
                                 name= str_link_type,
                                 source=src, target=tgt,
                                 header=header)

                link['FILL_COLOR'] = Qt.black

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

    # end of with

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
# end of def


def read_json(fpath):
    with codecs.open(fpath, "r", encoding="utf-8") as fin:
        d = json.loads(fin.read())
    return Network.from_dict(d)


def write_network(net, fpath):
    file_name_ext = os.path.basename(fpath)
    file_name_ext = file_name_ext.casefold()

    if file_name_ext.endswith('.sif'):
        write_sif(net, fpath)
    elif file_name_ext.endswith('.json'):
        write_json(net, fpath)
    else:
        raise ValueError("Unsupported file type: %s" % (file_name_ext))


def write_sif(net, fpath):
    with codecs.open(fpath, "w", encoding="utf-8") as fout:
        for iden, link in net.links.items():
            if 'SELFLOOP' in link.ITEM_TYPE:
                args = (link.node.iden, link.name, link.node.iden)
            else:
                args = (link.source.iden, link.name, link.target.iden)
            fout.write("%s\t%s\t%s\n"%args)


def write_json(net, fpath):
    with codecs.open(fpath, "w", encoding="utf-8") as fout:
        fout.write(json.dumps(net.to_dict()))


def write_image(net,
                fpath,
                is_transparent=True,
                quality=-1,
                scale_width=100, scale_height=100,
                dpi_width=350, dpi_height=350,
                pad_width=10, pad_height=10):


    fname, fext = extract_name_and_ext(fpath)

    scene = net.scene
    scene.clearSelection()
    brect = scene.itemsBoundingRect()
    brect.adjust(-pad_width, -pad_height, +2*pad_width, +2*pad_height)

    image = QImage((scale_width/100.0)*brect.width(),
                   (scale_height/100.0)*brect.height(),
                   QImage.Format_ARGB32_Premultiplied)

    # [REF] http://stackoverflow.com/a/13425280/4136588
    # dpm = 300 / 0.0254 # ~300 DPI
    dpm_width = dpi_width / 0.0254
    dpm_height = dpi_height / 0.0254
    image.setDotsPerMeterX(dpm_width)
    image.setDotsPerMeterY(dpm_height)

    bbrush = scene.backgroundBrush()

    painter = QPainter(image)
    if not is_transparent or fext in ['jpeg']:
        image.fill(Qt.white)
        painter.setPen(Qt.NoPen)
        painter.setBrush(bbrush.color())
        painter.drawRect(0, 0, image.width(), image.height())
    elif fext in ['png']:
        image.fill(bbrush.color())

    painter.setRenderHints(QPainter.TextAntialiasing
                           | QPainter.Antialiasing
                           | QPainter.SmoothPixmapTransform
                           | QPainter.HighQualityAntialiasing)

    scene.render(painter, source=brect)
    image.save(fpath, fext.upper(), quality)
    painter.end()


