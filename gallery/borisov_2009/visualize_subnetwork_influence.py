import os

import networkx as nx
from networkx import shortest_paths as nxsp

import pandas as pd
from nezzle.fileio import write_image

from qtpy.QtGui import QFont
from qtpy.QtGui import QColor

from nezzle.fileio import write_image
from nezzle.graphics import LabelClassFactory

TextLabel = LabelClassFactory.create('TEXT_LABEL')

dpath = os.path.dirname(__file__)

outputs = ['ERK', 'AKT']
inputs = ["EGF", "I"]


influence_erk = pd.read_csv(os.path.join(dpath, "influence_erk.csv"),
                            header=None, index_col=0, squeeze=True)
influence_erk = influence_erk.sort_values(ascending=False)
influence_erk = influence_erk.index.tolist()

influence_akt = pd.read_csv(os.path.join(dpath, "influence_akt.csv"),
                            header=None, index_col=0, squeeze=True)
influence_akt = influence_akt.sort_values(ascending=False)
influence_akt = influence_akt.index.tolist()

influence_comp = pd.read_csv(os.path.join(dpath, "influence_comp.csv"),
                             header=None, index_col=0, squeeze=True)
influence_comp = influence_comp.sort_values(ascending=False)
influence_comp = influence_comp.index.tolist()

influences = {'ERK': influence_erk,
              'AKT': influence_akt,
              'COMP': influence_comp}
              
influence = None

for node in (outputs + inputs):
    if node in influence_erk:
        influence_erk.remove(node)
        
    if node in influence_akt:
        influence_akt.remove(node)

color_flatten = '#d8d8d8'

def shortest_path_length_to_nodeset(dg, src, ns):
    """Compute the length of the shortest path
       from source to a set of nodes.
       
       It returns the minimum length of the shortest path
       between source and each node in the nodeset.

       Args:
        dg:
        src:
        ns:
    """
    min_spl = None
    node_min_spl = None
    for node in ns:
        try:
            spl = nxsp.shortest_path_length(dg, src, node)
            print(src, node, spl)
            if not min_spl or spl < min_spl:
                min_spl = spl
                node_min_spl = node
        except nx.NetworkXNoPath:    
            continue
    # end of for
    
    return min_spl, node_min_spl

def add_distance_text(net, node, output):
    dist = nxsp.shortest_path_length(net.nxdg, node.iden, output)
    label = net.labels[node.iden]
    label['TEXT'] = "%s[%d]"%(label['TEXT'], dist)

def visualize_subnetwork(net_sub, sub_nodes, output):
    print(sub_nodes)
    for iden, link in net_sub.links.items():
        link['FILL_COLOR'] = color_flatten
        link.setZValue(-1)
    
    # Decorate the link of the subnetwork including the output.
    nxdg_sub = net_sub.nxdg.subgraph(sub_nodes + [output])
    for source, target, data in nxdg_sub.edges(data=True):    
        link = data['VIS']
        link['FILL_COLOR'] = 'black'
        link.width = 2.5
        link.setZValue(1)
    
    # Decorate the nodes.
    for iden, node in net_sub.nodes.items():
        if iden in outputs:
            node['FILL_COLOR'] = 'white'
            node['BORDER_COLOR'] = 'red'
            node.setZValue(1)
        elif iden in inputs:
            node['FILL_COLOR'] = 'white'
            node['BORDER_COLOR'] = 'blue'
            node.setZValue(1)
        elif iden in sub_nodes:
            node['FILL_COLOR'] = 'yellow'
            node['BORDER_COLOR'] = 'black'
            node.setZValue(1)
        else:
            node['FILL_COLOR'] = color_flatten
            node['BORDER_COLOR'] = color_flatten
            node.setZValue(-1)

    #Denote the distances.
    """
    for iden, node in net_sub.nodes.items():
        if iden in sub_nodes:
            add_distance_text(net_sub, node, output)
    """
    #visualize_shortest_path(net_sub, shortest_path_io)
            
    # Resize nodes according to the sizes of labels.
    nodes_emphasized = sub_nodes + inputs + outputs
    for iden, label in net_sub.labels.items():
        node = label.parentItem()
        label['FONT_SIZE'] *= 0.8
        if node.iden in nodes_emphasized:
            label['TEXT_COLOR'] = "black"
        else:
            label['TEXT_COLOR'] = "#9b9b9b"
            
        rect = label.boundingRect()
        label.setPos(-rect.width() / 2, -rect.height() / 2)
        if node.iden in nodes_emphasized:
            node.width = 1.1*rect.width()
            node.height = 1.1*rect.height()
        else:            
            node.width = 1.1*rect.width()
            node.height = 1.1*rect.height()
            
def visualize_shortest_path(net, nodes_sp):
    """ Emphasize the shortest path in nezzle.graphics.Network.
    
        Args:
            net: nezzle.graphics.Network
                Network object in nezzle.
            nodes_sp: iterable
                Node names (str) in the shortest path.
    """
    
    # Create a subnetwork consisting of the nodes in the shortest path.
    nxdg_sub = net.nxdg.subgraph(nodes_sp)  
    for source, target, data in nxdg_sub.edges(data=True):
        link = data['VIS']
        link['FILL_COLOR'] = 'red'
        link.width = 4
        link.setZValue(1)
    
    for iden, node in net.nodes.items():
        if iden in nodes_sp:
            node['FILL_COLOR'] = 'yellow'
            node['BORDER_COLOR'] = 'red'
            label = net.labels[node.iden]
            label['TEXT_COLOR'] = 'red'
            label['FONT_BOLD'] = True
            node.setZValue(1)
 
def update(nav, net):
    global influence
    output = 'COMP'
    influence = influences[output]  # List object, not pd.Series
    
    for i in range(0, len(influence)+1):
        sub_nodes = influence[:i]    
        net_sub = net.copy()
        net_sub.name = 'borisov_2009_influence_%s_%02d'%(output.lower(), i)
        visualize_subnetwork(net_sub, sub_nodes, output)
        fname = "%s.jpeg"%(net_sub.name)
        fpath_img = os.path.join(dpath, fname)
        write_image(net_sub, fpath_img,
                    scale_width=200, scale_height=200,
                    dpi_width=600, dpi_height=600,)
        nav.append_item(net_sub)

    