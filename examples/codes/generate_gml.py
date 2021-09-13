import networkx as nx

G = nx.Graph()
G.add_edge(0, 1, weight=0.1, label='edge',
           graphics={'width': 8.0,
                     'fill': '"#0000ff"',
                     'type': r"line",
                     'line': "",
                     'sourceArrow': 0,
                     'targetArrow': r"delta"})

G.add_edge(1, 0, weight=0.5, label='edge',
           graphics={'width': 8.0,
                     'fill': '"#0000ff"',
                     'type': r"quadCurve",
                     'line': "",
                     'sourceArrow': 0,
                     'targetArrow': "delta"})

nx.set_node_attributes(G, {
    0: {'x': -100.0, 'y': 0.0,
        'w': 50.0, 'h': 50.0,
        'type': r"ellipse",
        'fill': r"#ffff00",
        'outline': r"#666666",
        "width": 4},
    1: {'x': 100.0, 'y': 0.0,
        'w': 50.0, 'h': 50.0,
        'type': r"rectangle",
        'fill': r"#ff9933",
        'outline': r"#000000",
        "width": 4}
    },
    'graphics')

nx.set_node_attributes(G, {0: "A", 1: "B"}, "label")
nx.write_gml(G, 'network2.gml')