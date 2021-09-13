import numpy as np
import networkx as nx


def layout(net, layout_func, scale=None, center=None):
    if not scale:
        coords = np.zeros((len(net.nodes), 2), dtype=np.float)
        for i, (iden, attr) in enumerate(net.nxdg.nodes_iter(data=True)):
            node = attr['GRAPHICS']
            coords[i, :] = node.x(), node.y()

        size_coords = coords.max(axis=0) - coords.min(axis=0)
        scale = np.ceil(np.max(size_coords))

    res = layout_func(net.nxdg, scale=scale, center=center)

    for iden, pos in res.items():
        node = net.nxdg.node[iden]['GRAPHICS']
        node.setX(pos[0])
        node.setY(pos[1])


