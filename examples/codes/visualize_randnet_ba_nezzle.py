import os
import os.path as osp
import time

import numpy as np
import pandas as pd
import networkx as nx

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import StraightLink
from nezzle.graphics import Network
from nezzle.io.io import write_image


def create_network(G):
    n = G.number_of_nodes()

    xlim = 500 + 200 * (np.log2(n) - 6)
    ylim = 500 + 200 * (np.log2(n) - 6)

    pos_x = np.random.normal(0, xlim, n)  # x-coordinates
    pos_y = np.random.normal(0, ylim, n)  # y-coordinates

    net = Network("")

    for i, id_node in enumerate(G.nodes):
        node = EllipseNode(id_node, 40, 40, pos=QPointF(pos_x[i], pos_y[i]))
        node["FILL_COLOR"] = Qt.white
        node["BORDER_COLOR"] = Qt.black
        node["BORDER_WIDTH"] = 2

        label = TextLabel(node, str(node.iden))
        label["FONT_SIZE"] = 12
        label["TEXT_COLOR"] = Qt.black
        label.align()

        net.add_node(node)

    for edge in G.edges:
        id_src = edge[0]
        id_tgt = edge[1]
        src = net.nodes[id_src]
        tgt = net.nodes[id_tgt]
        link = StraightLink("%s-%s"%(id_src, id_tgt), src, tgt, width=4)        
        link["FILL_COLOR"] = QColor(255, 0, 0, 20)   
        net.add_link(link)

    return net


def update(nav, net):
    
    dpath = osp.join(osp.dirname(__file__), "nezzle-randnet-ba-results")
    os.makedirs(dpath, exist_ok=True)

    results = []
    num_repeats = 5
    for r in range(num_repeats):
        for i in range(6):
            n = 2 ** (i + 6)
            for j in range(1, 6):
                m = j
                net_name = "nezzle-ba-n%d-m%d" % (n, m)
                print(net_name)

                G = nx.barabasi_albert_graph(n=n, m=m)
                print("- num. nodes:", G.number_of_nodes())
                print("- num. edges:", G.number_of_edges())

                t_beg = time.time()
                net = create_network(G)
                net.name = net_name

                fpath = osp.join(dpath, "%s.jpg"%(net.name))
                write_image(net,
                            fpath,
                            transparent=False,
                            image_width=512, image_height=512,
                            dpi_width=96, dpi_height=96)

                t_end = time.time()
                et = t_end - t_beg  # Execution time

                results.append({"name": net_name,
                                "trial": r,
                                "n": n,
                                "m": m,
                                "et": et})

                print("- execution time: %.3f sec." % (et), end="\n\n")
            # end of for
        # end of for
    # end of for

    df = pd.DataFrame(results)
    df.to_csv(osp.join(dpath, "nezzle-ba-results.csv"), index=False)

