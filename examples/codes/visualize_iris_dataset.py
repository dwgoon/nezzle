import os
import os.path as osp
from datetime import datetime

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import moviepy.editor as mpy

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import Network
from nezzle.io.io import write_image


class MeanPairwiseDistances(nn.Module):

    def __init__(self, pos, device="cpu"):
        super().__init__()

        self.pos = nn.Parameter(torch.tensor(pos),
                                requires_grad=True)

        self.pos = self.pos.to(device)

    def forward(self):
        return F.pdist(self.pos).mean()


def create_network(name, df):
    net = Network(name)

    for i, (pc1, pc2, target) in df.iterrows():
        x = 500 * pc1
        y = 500 * pc2

        node = EllipseNode(i, 40, 40, pos=QPointF(x, y))
        fill_color = Qt.white
        if target == "setosa":
            fill_color = Qt.red
        elif target == "versicolor":
            fill_color = Qt.green
        elif target == "virginica":
            fill_color = Qt.blue

        node["FILL_COLOR"] = fill_color
        node["BORDER_COLOR"] = Qt.black
        node["BORDER_WIDTH"] = 2

        label = TextLabel(node, str(node.iden))
        label["FONT_SIZE"] = 12
        label["TEXT_COLOR"] = Qt.black
        label.align()

        net.add_node(node)

    return net


def create_movie(fpaths, fout):
    clips = []
    duration = 0.05
    for (epoch, fpath) in fpaths:
        img_clip = mpy.ImageClip(fpath)
        img_clip = img_clip.set_duration(duration)
        img_clip = img_clip.resize(width=412, height=412)
        img_clip = img_clip.margin(100, color=(255, 255, 255))

        txt_clip = mpy.TextClip("Epoch=%04d"%(epoch), fontsize=16, color='black')
        txt_clip = txt_clip.set_duration(duration)
        txt_clip = txt_clip.set_position(("center", "bottom"))

        clip = mpy.CompositeVideoClip([img_clip, txt_clip], bg_color=(255, 255, 255))
        clips.append(clip)

    concat_clip = mpy.concatenate_videoclips(clips,
                                             bg_color=(255, 255, 255),
                                             method="compose")
    concat_clip.write_gif(fout, fps=10)


def update(nav, net):

    iris = load_iris()
    print(iris.data.shape)

    df_data = pd.DataFrame(iris.data, columns=iris.feature_names)
    scaler = StandardScaler()
    result = scaler.fit_transform(df_data)
    df_scaled = pd.DataFrame(result, columns=iris.feature_names)

    pca = PCA(n_components=2)
    result = pca.fit_transform(df_scaled)
    df_pc = pd.DataFrame(result, columns=["pc1", "pc2"])

    target = pd.DataFrame(iris.target, columns=['type'])
    target['type'] = target['type'].apply(lambda x: iris.target_names[x])
    df = pd.concat([df_pc, target], axis=1)

    net = create_network("Iris dataset (PCA)", df)
    nav.append_item(net)

    num_nodes = len(net.nodes)
    positions = np.zeros((num_nodes, 2))

    for i, (iden, node) in enumerate(net.nodes.items()):
        positions[i, :] = (node["POS_X"], node["POS_Y"])
    # end of for

    # Layout by maximizing mean pairwise distances (MPD) (== minimizing the negative MPD).
    model = MeanPairwiseDistances(positions)
    optimizer = optim.SGD(model.parameters(), lr=1e2, momentum=0.25)

    dpath = osp.join(osp.dirname(__file__), "iris-layout-dynamics-results")
    os.makedirs(dpath, exist_ok=True)

    fpaths_img = []
    n_epoch = 1200
    for epoch in range(n_epoch):
        optimizer.zero_grad()

        loss = model()
        print("[Epoch #%d] Loss: %.3f" % (epoch + 1, loss.item()))

        loss.backward()
        optimizer.step()

        if epoch % 5 == 0:
            positions = model.pos.cpu().detach().numpy()

            net = net.copy()
            for i, (iden, node) in enumerate(net.nodes.items()):
                node["POS_X"] = positions[i, 0]
                node["POS_Y"] = positions[i, 1]

            fpath = osp.join(dpath, "iris-layout-%04d.jpg" % (epoch))
            fpaths_img.append((epoch, fpath))
            write_image(net,
                        fpath,
                        scale_width=200,
                        scale_height=200)
        # end of if
    # end of for

    for epoch in range(n_epoch, 2*n_epoch):
        optimizer.zero_grad()

        loss = -1 * model()
        print("[Epoch #%d] Loss: %.3f" % (epoch + 1, loss.item()))

        loss.backward()
        optimizer.step()

        if epoch % 5 == 0:
            positions = model.pos.cpu().detach().numpy()

            net = net.copy()
            for i, (iden, node) in enumerate(net.nodes.items()):
                node["POS_X"] = positions[i, 0]
                node["POS_Y"] = positions[i, 1]

            fpath = osp.join(dpath, "iris-layout-%03d.jpg" % (epoch))
            fpaths_img.append((epoch, fpath))
            write_image(net, fpath, scale_width=100, scale_height=100)
        # end of if
    # end of for

    create_movie(fpaths_img, osp.join(dpath, "iris-layout-dynamics.gif"))
    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    net.name = "%s (%s)"%(net.name, time_stamp)
    nav.append_item(net)
