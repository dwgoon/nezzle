import os
import os.path as osp

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import moviepy.editor as mpy
from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF

from nezzle.io.io import write_image
from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import CurvedLink
from nezzle.graphics import Triangle, Hammer
from nezzle.graphics import Network


class MeanPairwiseDistances(nn.Module):

    def __init__(self, pos, device="cpu"):
        super().__init__()

        self.pos = nn.Parameter(torch.tensor(pos),
                                requires_grad=True)

        self.pos = self.pos.to(device)

    def forward(self):
        return F.pdist(self.pos).mean()


def create_movie(fpaths, fout):
    clips = []
    duration = 0.05
    for (epoch, fpath) in fpaths:
        img_clip = mpy.ImageClip(fpath)
        img_clip = img_clip.set_duration(duration)
        img_clip = img_clip.resize(width=412, height=412)
        img_clip = img_clip.margin(100, color=(255, 255, 255))
        img_clip = img_clip.resize(width=256, height=256)

        txt_clip = mpy.TextClip("Epoch=%03d"%(epoch), fontsize=16, color='black')
        txt_clip = txt_clip.set_duration(duration)
        txt_clip = txt_clip.set_position(("center", "bottom"))

        clip = mpy.CompositeVideoClip([img_clip, txt_clip], bg_color=(255, 255, 255))
        clips.append(clip)

    concat_clip = mpy.concatenate_videoclips(clips,
                                             bg_color=(255, 255, 255),
                                             method="compose")
    concat_clip.write_gif(fout, fps=10)


def update(nav, net):
    net = Network("10-node network (before layout)")

    num_nodes = 10
    num_links = 20
    positions = np.random.uniform(-10, 10, size=(num_nodes, 2))

    for i, pos in enumerate(positions):
        node = EllipseNode(str(i), 40, 40, pos=QPointF(pos[0], pos[1]))
        node["FILL_COLOR"] = Qt.white
        node["BORDER_COLOR"] = Qt.black
        node["BORDER_WIDTH"] = 2

        label = TextLabel(node, node.iden)
        label["FONT_SIZE"] = 20
        label.align()

        net.add_node(node)
        net.add_label(label)
        # end of for

    connections = np.random.randint(0, num_nodes, size=(num_links, 2))
    set_links = set()
    for i, conn in enumerate(connections):
        src = net.nodes[str(conn[0])]
        tgt = net.nodes[str(conn[1])]

        if (src.iden, tgt.iden) in set_links:
            continue

        if np.random.randn() < 0.5:
            head = Triangle(width=10, height=10, offset=4)
            link = CurvedLink("LINK%d(%s+%s)"%(i, src.iden, tgt.iden), src, tgt, width=4, head=head)

        else:
            head = Hammer(width=16, height=3, offset=4)
            link = CurvedLink("LINK%d(%s-%s)"%(i, src.iden, tgt.iden), src, tgt, width=4, head=head)

        link["FILL_COLOR"] = Qt.black
        link["CP_POS_X"] = -10
        link["CP_POS_Y"] = -70

        net.add_link(link)
        set_links.add((src.iden, tgt.iden))
    # end of for

    nav.append_item(net)

    # Layout by maximizing mean pairwise distances (MPD) (== minimizing the negative MPD).
    model = MeanPairwiseDistances(positions)
    optimizer = optim.SGD(model.parameters(), lr=1e-1, momentum=0.9)

    dpath = osp.join(osp.dirname(__file__), "randnet-layout-by-pytorch-results")
    os.makedirs(dpath, exist_ok=True)

    fpaths_img = []
    n_epoch = 2000
    for epoch in range(n_epoch):
        optimizer.zero_grad()

        loss = -1 * model()
        print("[Epoch #%d] Loss: %.3f" % (epoch + 1, loss.item()))

        loss.backward()
        optimizer.step()

        if epoch % 5 == 0:
            positions = model.pos.cpu().detach().numpy()

            net = net.copy()
            for iden, node in net.nodes.items():
                i = int(iden)
                node["POS_X"] = positions[i, 0]
                node["POS_Y"] = positions[i, 1]

            fpath = osp.join(dpath, "layout-%03d.jpg" % (epoch))
            fpaths_img.append((epoch, fpath))
            write_image(net,
                        fpath,
                        scale_width=200,
                        scale_height=200)
        # end of if
    # end of for

    create_movie(fpaths_img, osp.join(dpath, "layout-dynamics.gif"))

    net.name = "10-node network (after layout)"
    nav.append_item(net)
