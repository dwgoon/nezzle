

def update(nav, net):

    for iden, node in net.nodes.items():
        node["BORDER_WIDTH"] = 2
        node["BORDER_COLOR"] = "black"
        node["FILL_COLOR"] = "white"
        node["WIDTH"] = 30
        node["HEIGHT"] = 30

    for iden, label in net.labels.items():
        label["FONT_FAMILY"] = "Arial"
        label["FONT_SIZE"] = 16
        label["FONT_COLOR"] = "black"
        label.align()
