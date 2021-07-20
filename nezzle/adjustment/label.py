

def _set_displacement(pos, dp):
    dp_x = dp
    dp_y = dp

    if 'top' in pos:
        dp_y *= -1

    if 'left' in pos:
        dp_x *= -1

    return dp_x, dp_y


def _align_label_center(net):
    for label in net.labels:
        rect = label.boundingRect()
        label.setPos(-rect.width() / 2, -rect.height() / 2)


def align_label(net, pos='bottomright', dp=7):
    """
    Align labels with the position relative to their parent nodes
    The alignment should be updated after changing fonts,
    because setting new fonts changes the size of labels, which invalidates
    the previous alignment.
    """

    if pos == 'center':
        return _align_label_center(net)

    dp_x, dp_y = _set_displacement(pos, dp)

    for label in net.labels:
        node = label.parent
        #labels.setPos(nodes._radius + dp_x, nodes._radius + dp_y)
        label.setPos(dp_x, dp_y)




