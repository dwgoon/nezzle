import nezzle


def search_links(net, substr):
    """Find links whose identity string contain the given substring.

    Args:
        net: nezzle.graphics.Network
            Network object whose links are searched.
        substr: str
            Substring to search in the identity string of a link (link.iden).

    Returns:
        links: list
            List of links whose identity strings contain the substring.

    """
    links_found = []
    for iden, link in net.links.items():
        if isinstance(link, nezzle.graphics.SelfloopLink):
            if substr in link.node.iden:
                links_found.append(link)
            else:
                continue
        elif substr in link.target.iden or substr in link.source.iden:
            links_found.append(link)

    return links_found


def search_links_target(net, substr):
    links_found = []
    for src, tgt, data in net.nxdg.edges(data=True):
        link = data['GRAPHICS']
        if isinstance(link, nezzle.graphics.SelfloopLink):
            if substr in link.node:
                links_found.append(link)
        elif substr in link.target.iden:
            links_found.append(link)
    # end of for
    return links_found