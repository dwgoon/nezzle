import numpy as np
from scipy.integrate import odeint
import moviepy.editor as mpy

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import CurvedLink
from nezzle.graphics import Triangle, Hammer
from nezzle.graphics import Network
from nezzle.fileio import write_image


def create_network(pos_x, pos_y, s):
    color_white = np.array([255, 255, 255, 0])
    color_up = np.array([255, 0, 0, 0])
    color_dn = np.array([0, 0, 255, 0])

    net = Network('2NNFL')
    src = EllipseNode('A', 40, 40, pos=QPointF(pos_x[0], pos_y[0]))
    tgt = EllipseNode('B', 40, 40, pos=QPointF(pos_x[1], pos_y[1]))

    net.add_node(src)
    net.add_node(tgt)

    head = Triangle(width=10, height=10, offset=4)
    link1 = CurvedLink("LINK1", src, tgt, width=4, head=head)
    link1["FILL_COLOR"] = Qt.black
    link1["CP_POS_X"] = -10
    link1["CP_POS_Y"] = -50

    head = Hammer(width=16, height=3, offset=4)
    link2 = CurvedLink("LINK2", tgt, src, width=4, head=head)
    link2["FILL_COLOR"] = Qt.black
    link2["CP_POS_X"] = 10
    link2["CP_POS_Y"] = 50

    net.add_link(link1)
    net.add_link(link2)

    for i, node in enumerate([src, tgt]):
        abs_s = np.abs(s)
        norm_abs_s = abs_s / abs_s.max()
        if s[i] > 0:
            color = color_white + norm_abs_s[i] * (color_up - color_white)
        elif s[i] <= 0:
            color = color_white + norm_abs_s[i] * (color_dn - color_white)

        color[3] = 255
        node["FILL_COLOR"] = QColor(*color)
        node["BORDER_COLOR"] = Qt.black
        node["BORDER_WIDTH"] = 2
        node["WIDTH"] = node["HEIGHT"] = 20 + 50 * norm_abs_s[i]

        label_name = TextLabel(node, node.iden)
        label_name["FONT_SIZE"] = 10 + 30 * norm_abs_s[i]
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
    nav.clear()

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

    sol = sol - np.median(sol)

    pos_x = np.array([-80.0, 80.0])
    pos_y = np.array([0.0, 0.0])

    fpaths = []
    for i, s in enumerate(sol):
        net = create_network(pos_x, pos_y, s)
        fpath = "2nnfl-dynamics-%03d.png"%(i)
        fpaths.append(fpath)
        write_image(net, fpath, transparent=False, scale_width=200, scale_height=200)
    # end of for

    create_movie(fpaths, "2nnfl-dynamics.gif")