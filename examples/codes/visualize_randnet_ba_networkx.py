import os
import os.path as osp
import time

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

    
if __name__ == "__main__":
    
    dpi = 96
    width = 512 / dpi
    height = 512 / dpi
    plt.ioff()

    dpath = osp.join(osp.dirname(__file__), "networkx-randnet-ba-results")
    os.makedirs(dpath, exist_ok=True)

    results = []
    num_repeats = 5
    for r in range(num_repeats):
        for i in range(6):
            n = 2 ** (i + 6)
            for j in range(1, 6):
                m = j
                net_name = "networkx-ba-n%d-m%d" % (n, m)
                print(net_name)
    
                G = nx.barabasi_albert_graph(n=n, m=m)
                print("- num. nodes:", G.number_of_nodes())
                print("- num. edges:", G.number_of_edges())
    
                # Generate random xy-coordinates
                xylim = 500 + 200 * (np.log2(n) - 6)
                pos = {i: xy for i, xy in enumerate(np.random.normal(0, xylim, (n, 2)))}  
                
                t_beg = time.time()
    
                fig = plt.figure(figsize=(xylim, xylim), frameon=False)            

                
                nx.draw_networkx_edges(G, pos,
                                       width=1,
                                       edge_color="#FF0000",
                                       alpha=0.078125)
                
                nx.draw_networkx_nodes(G, pos,       
                                       node_size=5,
                                       linewidths=0.25,
                                       edgecolors="#000000",
                                       node_color="#FFFFFF",
                                       alpha=0.8)
                
                nx.draw_networkx_labels(G, pos,
                                        alpha=0.025,
                                        font_size=4,
                                        TEXT_COLOR="#000000",
                                        horizontalalignment="center",
                                        verticalalignment="center")
    
                plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0)

                fig.set_size_inches(width, height)
                fpath = osp.join(dpath, "%s.jpg"%(net_name))
                plt.savefig(fpath,
                            format="JPG",
                            dpi=dpi)
                plt.close()
    
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
    df.to_csv(osp.join(dpath, "networkx-ba-results.csv"), index=False)