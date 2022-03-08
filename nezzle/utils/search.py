import nezzle


def search_edges(net, substr):
    """Find edges whose identity string contain the given substring.

    Args:
        net: nezzle.graphics.Network
            Network object whose edges are searched.
        substr: str
            Substring to search in the identity string of a edge (edge.iden).

    Returns:
        edges: list
            List of edges whose identity strings contain the substring.

    """
    edges_found = []
    for iden, edge in net.edges.items():
        if isinstance(edge, nezzle.graphics.SelfloopEdge):
            if substr in edge.node.iden:
                edges_found.append(edge)
            else:
                continue
        elif substr in edge.target.iden or substr in edge.source.iden:
            edges_found.append(edge)

    return edges_found


def search_edges_target(net, substr):
    edges_found = []
    for src, tgt, data in net.nxgraph.edges(data=True):
        edge = data['GRAPHICS']
        if isinstance(edge, nezzle.graphics.SelfloopEdge):
            if substr in edge.node:
                edges_found.append(edge)
        elif substr in edge.target.iden:
            edges_found.append(edge)
    # end of for
    return edges_found