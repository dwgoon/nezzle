import os
import os.path as osp
import time

import numpy as np
import networkx as nx

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import StraightLink
from nezzle.graphics import Network
from nezzle.fileio import write_image


def create_network(n, m):
    G = nx.barabasi_albert_graph(n=n, m=m)

    print("Num. Nodes:", G.number_of_nodes())
    print("Num. Edges:", G.number_of_edges())

    xlim = 500 + 200 * (np.log2(n) - 6)
    ylim = 500 + 200 * (np.log2(n) - 6)

    pos_x = np.random.normal(0, xlim, n)  # x-coordinates
    pos_y = np.random.normal(0, ylim, n)  # y-coordinates

    t_beg = time.time()
    net = Network('ba-n%d-m%d'%(n, m))

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

    t_end = time.time()
    et = t_end - t_beg # Execution time

    return net, et


def update(nav, net):
    
    dpath = osp.join(osp.dirname(__file__), "temp-images")
    os.makedirs(dpath, exist_ok=True)

    execution_times = {}
    for i in range(2):
        n = 2 ** (i + 6)
        m = 2
        net, et = create_network(n, m)
        execution_times[net.name] = et
        print("%s: %.3f sec."%(net.name, et))
        fpath = osp.join(dpath, "%s.png"%(net.name))
        write_image(net,
                    fpath,
                    transparent=False,
                    scale_width=200, scale_height=200)

        nav.append_item(net)
    # end of for

