import os
import os.path as osp
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import moviepy.editor as mpy

from nezzle.fileio import write_image


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
    num_nodes = len(net.nodes)
    positions = np.zeros((num_nodes, 2))

    for i, (iden, node) in enumerate(net.nodes.items()):
        positions[i, :] = (node["POS_X"], node["POS_Y"])
    # end of for

    # Layout by maximizing mean pairwise distances (MPD) (== minimizing the negative MPD).
    model = MeanPairwiseDistances(positions)
    optimizer = optim.SGD(model.parameters(), lr=2e-1, momentum=0.5)

    dpath = osp.join(osp.dirname(__file__), "net-layout-by-pytorch-results")
    os.makedirs(dpath, exist_ok=True)

    fpaths_img = []
    n_epoch = 1000
    arr_loss = np.zeros(n_epoch)
    for epoch in range(n_epoch):
        optimizer.zero_grad()

        loss = -1 * model()
        print("[Epoch #%d] Loss: %.3f" % (epoch + 1, loss.item()))
        arr_loss[epoch] = loss.item()

        loss.backward()
        optimizer.step()

        if epoch % 5 == 0:
            positions = model.pos.cpu().detach().numpy()

            net = net.copy()
            for i, (iden, node) in enumerate(net.nodes.items()):
                node["POS_X"] = positions[i, 0]
                node["POS_Y"] = positions[i, 1]

            fpath = osp.join(dpath, "%s-layout-%03d.jpg" % (net.name, epoch))
            fpaths_img.append((epoch, fpath))
            write_image(net,
                        fpath,
                        scale_width=200,
                        scale_height=200)
        # end of if
    # end of for

    np.savetxt(osp.join(dpath, "loss_curve.csv"), arr_loss, delimiter=",")
    create_movie(fpaths_img, osp.join(dpath, "%s-layout-dynamics.gif")%(net.name))

    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    net.name = "%s (%s)"%(net.name, time_stamp)
    nav.append_item(net)
