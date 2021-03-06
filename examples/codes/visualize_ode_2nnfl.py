import os
import os.path as osp

import numpy as np
from scipy.integrate import odeint
import moviepy.editor as mpy

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import CurvedEdge
from nezzle.graphics import Triangle, Hammer
from nezzle.graphics import Network
from nezzle.io import write_image


def create_network(pos_x, pos_y, s):
    color_white = np.array([255, 255, 255, 0])
    color_up = np.array([255, 0, 0, 0])
    color_dn = np.array([0, 0, 255, 0])

    net = Network('2NNFL')
    src = EllipseNode('A', 40, 40, pos=QPointF(pos_x[0], pos_y[0]))
    trg = EllipseNode('B', 40, 40, pos=QPointF(pos_x[1], pos_y[1]))

    net.add_node(src)
    net.add_node(trg)

    head = Triangle(width=10, height=10, offset=4)
    edge1 = CurvedEdge("EDGE1", src, trg, width=4, head=head)
    edge1["FILL_COLOR"] = Qt.black
    edge1["CP_POS_X"] = -10
    edge1["CP_POS_Y"] = -50

    head = Hammer(width=16, height=3, offset=4)
    edge2 = CurvedEdge("EDGE2", trg, src, width=4, head=head)
    edge2["FILL_COLOR"] = Qt.black
    edge2["CP_POS_X"] = 10
    edge2["CP_POS_Y"] = 50

    net.add_edge(edge1)
    net.add_edge(edge2)

    for i, node in enumerate([src, trg]):

        if s[i] > 0.5:
            color = color_white + s[i] * (color_up - color_white)
        else:
            color = color_white + s[i] * (color_dn - color_white)

        color[3] = 255
        node["FILL_COLOR"] = QColor(*color)
        node["BORDER_COLOR"] = Qt.black
        node["BORDER_WIDTH"] = 2
        node["WIDTH"] = node["HEIGHT"] = 20 + 50 * s[i]

        label_name = TextLabel(node, node.iden)
        label_name["FONT_SIZE"] = 10 + 30 * s[i]
        label_name["TEXT_COLOR"] = Qt.white
        label_name.align()

        lightness = QColor(node["FILL_COLOR"]).lightness()
        if lightness < 200:
            label_name["TEXT_COLOR"] = Qt.white
            label_name["FONT_BOLD"] = True
        else:
            label_name["TEXT_COLOR"] = Qt.black
            label_name["FONT_BOLD"] = False

        net.add_label(label_name)
    # end of for
    return net


def create_movie(fpaths, fout):
    clips = []
    for fpath in fpaths:
        img = mpy.ImageClip(fpath).set_duration(0.2)
        clips.append(img)

    concat_clip = mpy.concatenate_videoclips(clips,
                                             bg_color=(255, 255, 255),
                                             method="compose")
    concat_clip.write_gif(fout, fps=30)


def update(nav, net):

    # Solve the ODE of 2-node negative feedback loop model
    def ode(y, t):
        dydt = np.zeros(y.shape)
        ka1 = 0.8
        Km1 = 1.0
        kd1 = 0.06
        ka2 = 0.95
        Km2 = 1.0
        kd2 = 0.7
        dydt[0] = ka1/(y[1]**4 + Km1**4) - kd1*y[0]
        dydt[1] = ka2*y[1]*y[0]**2/(y[0]**2 + Km2**2) - kd2*y[1]
        return dydt

    t = np.arange(0, 100, 1)
    y0 = np.array([1., 1.])
    sol = odeint(ode, y0, t)

    norm_s = sol / sol.max()

    pos_x = np.array([-80.0, 80.0])
    pos_y = np.array([0.0, 0.0])

    dpath = osp.join(osp.dirname(__file__), "2nnfl-dynamics-results")
    os.makedirs(dpath, exist_ok=True)

    fpaths = []
    for i, s in enumerate(norm_s):
        net = create_network(pos_x, pos_y, s)
        fpath = osp.join(dpath, "2nnfl-dynamics-%03d.png"%(i))
        fpaths.append(fpath)
        write_image(net, fpath, transparent=False, scale_width=200, scale_height=200)
    # end of for

    create_movie(fpaths, osp.join(dpath, "2nnfl-dynamics.gif"))