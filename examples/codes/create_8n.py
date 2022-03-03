import pandas as pd

from qtpy.QtCore import QPointF

from nezzle.graphics import EllipseNode
from nezzle.graphics import TextLabel
from nezzle.graphics import StraightLink
from nezzle.graphics import Triangle, Hammer
from nezzle.graphics import Network


def update(nav, net):
    node_positions = [
        {"ID": "A", "POS_X": 455.6, "POS_Y": 511.7},
        {"ID": "C", "POS_X": 517.7, "POS_Y": 570.3},
        {"ID": "D", "POS_X": 409.5, "POS_Y": 580.0},
        {"ID": "G", "POS_X": 380.5, "POS_Y": 483.8},
        {"ID": "B", "POS_X": 538.3, "POS_Y": 486.9},
        {"ID": "E", "POS_X": 594.9, "POS_Y": 424.8},
        {"ID": "H", "POS_X": 518.3, "POS_Y": 642.4},
        {"ID": "F", "POS_X": 598.0, "POS_Y": 601.2}
    ]

    link_types = [
        {"SOURCE": "A", "TARGET": "C", "INTERACTION": "INHIBITS"},
        {"SOURCE": "A", "TARGET": "D", "INTERACTION": "ACTIVATES"},
        {"SOURCE": "A", "TARGET": "G", "INTERACTION": "ACTIVATES"},
        {"SOURCE": "B", "TARGET": "A", "INTERACTION": "ACTIVATES"},
        {"SOURCE": "B", "TARGET": "E", "INTERACTION": "ACTIVATES"},
        {"SOURCE": "C", "TARGET": "B", "INTERACTION": "ACTIVATES"},
        {"SOURCE": "C", "TARGET": "H", "INTERACTION": "INHIBITS"},
        {"SOURCE": "F", "TARGET": "C", "INTERACTION": "ACTIVATES"}
    ]

    df_node_pos = pd.DataFrame(node_positions)
    df_link_types = pd.DataFrame(link_types)

    net = Network('A simple 8-node network')

    for i, row in df_node_pos.iterrows():
        node = EllipseNode(row["ID"], 30, 30, pos=QPointF(row["POS_X"], row["POS_Y"]))
        node["BORDER_WIDTH"] = 2
        node["BORDER_COLOR"] = "black"
        node["FILL_COLOR"] = "white"

        label = TextLabel(node, node.iden)
        label["FONT_FAMILY"] = "Arial"
        label["FONT_SIZE"] = 16
        label["TEXT_COLOR"] = "black"
        label.align()

        net.add_node(node)
        net.add_label(label)
    # end of for

    for i, row in df_link_types.iterrows():
        src = net.nodes[row["SOURCE"]]
        tgt = net.nodes[row["TARGET"]]

        if row["INTERACTION"] == "ACTIVATES":
            head = Triangle(width=10, height=10, offset=4)
            link = StraightLink("LINK(%s+%s)", src, tgt, width=4, head=head)
        else:
            head = Hammer(width=16, height=3, offset=4)
            link = StraightLink("LINK(%s-%s)", src, tgt, width=4, head=head)

        link["WIDTH"] = 2
        link["FILL_COLOR"] = "black"

        net.add_link(link)
    # end of for

    nav.append_item(net)