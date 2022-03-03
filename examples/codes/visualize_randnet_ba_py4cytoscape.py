import os
import os.path as osp
import time

import numpy as np
import pandas as pd
import networkx as nx

import py4cytoscape as p4c


def create_network(collection, name, G):
    n = G.number_of_nodes()

    xlim = 500 + 200 * (np.log2(n) - 6)
    ylim = 500 + 200 * (np.log2(n) - 6)

    pos_x = np.random.normal(0, xlim, n)  # x-coordinates
    pos_y = np.random.normal(0, ylim, n)  # y-coordinates

    p4c.create_network_from_networkx(G, title=name, collection=collection)

    # Update nodes
    node_ids = p4c.get_all_nodes()
    p4c.set_node_shape_default('ELLIPSE')   
    p4c.set_node_property_bypass(node_ids, "40", "NODE_WIDTH")    
    p4c.set_node_property_bypass(node_ids, "40", "NODE_HEIGHT")    
    p4c.set_node_property_bypass(node_ids, "#FFFFFF", "NODE_FILL_COLOR")    
    p4c.set_node_property_bypass(node_ids, "2", "NODE_BORDER_WIDTH")    
    p4c.set_node_property_bypass(node_ids, "#000000", "NODE_BORDER_PAINT")
    p4c.set_node_property_bypass(node_ids, pos_x.tolist(), "NODE_X_LOCATION")    
    p4c.set_node_property_bypass(node_ids, pos_y.tolist(), "NODE_Y_LOCATION")

    # Update labels
    p4c.set_node_property_bypass(node_ids, "12", "NODE_LABEL_FONT_SIZE")    
    p4c.set_node_property_bypass(node_ids, "#000000", "NODE_LABEL_COLOR")
    p4c.set_node_property_bypass(node_ids, "Center", "NODE_LABEL_POSITION")

    # Update edges
    edge_ids = p4c.get_all_edges()
    p4c.set_edge_property_bypass(edge_ids, "4", "EDGE_WIDTH")    
    p4c.set_edge_property_bypass(edge_ids, "#FF0000", "EDGE_PAINT")    
    p4c.set_edge_property_bypass(edge_ids, "20", "EDGE_TRANSPARENCY")


if __name__ == "__main__":
    
    print(p4c.cytoscape_ping())
    print(p4c.cytoscape_version_info())

    dpath = osp.join(osp.dirname(__file__), "cytoscape-randnet-ba-results")
    os.makedirs(dpath, exist_ok=True)

    results = []
    num_repeats = 1
    for r in range(num_repeats):        
        for i in range(6):
            n = 2 ** (i + 6)
            for j in range(1, 6):
                m = j
                net_name = "cytoscape-ba-n%d-m%d" % (n, m)
                print(net_name)
    
                G = nx.barabasi_albert_graph(n=n, m=m)
                print("- trial:", r + 1)
                print("- num. nodes:", G.number_of_nodes())
                print("- num. edges:", G.number_of_edges())
    
                t_beg = time.time()
                create_network("cytoscape-randnet-ba", net_name, G)
    
                fpath = osp.join(dpath, "%s.jpg"%(net_name))
                p4c.network_views.fit_content()
                
                res = p4c.export_image(fpath,
                                       type="JPG",
                                       units='pixels',
                                       zoom=100,
                                       width=512, height=512,
                                       resolution=300,
                                       overwrite_file=True)
    
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
    df.to_csv(osp.join(dpath, "cytoscape-ba-results.csv"), index=False)


