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


def create_network(pos_x, pos_y, state, norm_abs_state):
    color_white = np.array([255, 255, 255, 0])
    color_up = np.array([255, 0, 0, 0])
    color_dn = np.array([0, 0, 255, 0])

    net = Network('Lorenz network')
    x = EllipseNode('X', 40, 40, pos=QPointF(pos_x[0], pos_y[0]))
    y = EllipseNode('Y', 40, 40, pos=QPointF(pos_x[1], pos_y[1]))
    z = EllipseNode('Z', 40, 40, pos=QPointF(pos_x[2], pos_y[2]))

    net.add_node(x)
    net.add_node(y)
    net.add_node(z)

    head = Triangle(width=10, height=10, offset=4)
    edge1 = CurvedEdge("EDGE1", x, y, width=4, head=head)
    edge1["FILL_COLOR"] = Qt.black
    edge1["CP_POS_X"] = -10
    edge1["CP_POS_Y"] = -50

    head = Triangle(width=10, height=10, offset=4)
    edge2 = CurvedEdge("EDGE2", y, x, width=4, head=head)
    edge2["FILL_COLOR"] = Qt.black
    edge2["CP_POS_X"] = 10
    edge2["CP_POS_Y"] = 40
    
    head = Triangle(width=10, height=10, offset=4)
    edge3 = CurvedEdge("EDGE3", y, z, width=4, head=head)
    edge3["FILL_COLOR"] = Qt.black
    edge3["CP_POS_X"] = -28
    edge3["CP_POS_Y"] = -28
    
    head = Hammer(width=14, height=4, offset=4)
    edge4 = CurvedEdge("EDGE3", z, y, width=4, head=head)
    edge4["FILL_COLOR"] = Qt.black
    edge4["CP_POS_X"] = 45
    edge4["CP_POS_Y"] = 40
    
    head = Triangle(width=10, height=10, offset=4)
    edge5 = CurvedEdge("EDGE3", z, x, width=4, head=head)
    edge5["FILL_COLOR"] = Qt.black
    edge5["CP_POS_X"] = -45
    edge5["CP_POS_Y"] = 40
    
    net.add_edge(edge1)
    net.add_edge(edge2)
    net.add_edge(edge3)
    net.add_edge(edge4)
    net.add_edge(edge5)

    for i, node in enumerate([x, y, z]):
        if state[i] > 0.0:
            color = color_white + norm_abs_state[i] * (color_up - color_white)
        else:
            color = color_white + norm_abs_state[i] * (color_dn - color_white)

        color[3] = 255
        node["FILL_COLOR"] = QColor(*color)
        node["BORDER_COLOR"] = Qt.black
        node["BORDER_WIDTH"] = 2
        node["WIDTH"] = node["HEIGHT"] = 20 + 50 * norm_abs_state[i]

        label_name = TextLabel(node, node.iden)
        label_name["FONT_SIZE"] = 10 + 30 * norm_abs_state[i]
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
    concat_clip.write_gif(fout, fps=10)


def update(nav, net):

    # Solve the ODE of Lorenz system
    def ode(s, t):
        sigma = 10
        beta = 2.667
        rho = 28
        x, y, z = s
        return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]
    
    t = np.arange(0, 20, 0.1)
    y0 = np.array([0, 1, 1.05])
    s = odeint(ode, y0, t)

    abs_s = np.abs(s)
    norm_abs_s = abs_s / abs_s.max(axis=0)

    pos_x = np.array([-100.0, 100.0, 0.0])
    pos_y = np.array([0.0, 0.0, 120.0])

    dpath = osp.join(osp.dirname(__file__), "lorenz-dynamics-results")
    os.makedirs(dpath, exist_ok=True)

    fpaths = []
    for i, (state, norm_abs_state) in enumerate(zip(s, norm_abs_s)):
        net = create_network(pos_x, pos_y, state, norm_abs_state)
        fpath = osp.join(dpath, "lorenz-dynamics-%03d.png"%(i))
        fpaths.append(fpath)
        write_image(net, fpath, scale_width=200, scale_height=200)
    # end of for

    create_movie(fpaths, osp.join(dpath, "lorenz-dynamics.gif"))
