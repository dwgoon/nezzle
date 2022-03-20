import os
from os.path import join as pjoin
from os.path import dirname, abspath
import sys
import networkx as nx
import numpy as np
import pandas as pd

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtGui import QFont

import sfa
from sfv.visualizers import LinearVisualizer

from nezzle.io import write_image
from nezzle.utils import reload_modules


reload_modules()

dpath = os.path.dirname(__file__)


def visualize(nav, net, alg, data, mutations, targets):
    
    n2i = data.n2i
    n_nodes = len(n2i)
        
    b = np.zeros((n_nodes,), dtype=np.float)
    
    inds = []
    vals = []
    alg.apply_inputs(inds, vals)
    b[inds] = vals

    W_ctrl = alg.W.copy()
    x_ctrl, trj_ctrl = alg.propagate_iterative(
                                W_ctrl,
                                b,
                                b,
                                alg.params.alpha,
                                get_trj=False)

    # Apply perturbations
    W_pert = W_ctrl.copy()
    alg.apply_perturbations(targets, inds, vals, W_pert)
    
    # Mutations
    for mut in mutations:
        b[n2i[mut]] = 1
        W_pert[n2i[mut], :] *= 0
        W_pert[:, n2i[mut]] *= 10
    
    alg.W = W_pert

    b[inds] = vals
    x_pert, trj_pert = alg.propagate_iterative(W_pert, 
                                               b,
                                               b,
                                               alg.params.alpha,
                                               get_trj=False)

    act = x_pert - x_ctrl

    dF = W_pert*x_pert - W_ctrl*x_ctrl  # Change in signal flow

    
    font = QFont('Arial', 11)
    visualizer = LinearVisualizer()
    visualizer.visualize(net,
                         dF,
                         act,
                         data.A,
                         data.n2i,
                         lw_min=1.5,
                         lw_max=5,
                         pct_edge=90,
                         pct_act=90,
                         fix_act_label=False,
                         show_act=False,
                         font=font)
        
    for iden, node in net.nodes.items():
        node['BORDER_WIDTH'] = 2
        node['BORDER_COLOR'] = QColor(40, 40, 40)
        
    for iden, edge in net.edges.items():
        color = QColor(edge['FILL_COLOR'])
        color.setAlpha(70)
        edge['FILL_COLOR'] = color
    
    nav.append_item(net)


def update(nav, net):
    ds = sfa.DataSet()
    ds.create("BORISOV_2009")
    data = sfa.get_avalue(ds["BORISOV_2009"])
    
    algs = sfa.AlgorithmSet()
    alg = algs.create("SP")

    alg.params.alpha = 0.5
    alg.params.apply_weight_norm = True
    alg.params.use_rel_change = True
    
    mutations = ['PI3K']

    # Candidates: [['RAS', 'PIP3'], ['MEK', 'PDK1']]
    list_targets = [['RAS', 'PIP3']]
    val_inh = -10

    for i, targets in enumerate(list_targets):
        data.df_ptb.loc[targets, 'Value'] = val_inh
        data.A[data.n2i['RAF'], data.n2i['AKT']] = 0
        alg.data = data        
        alg.initialize()

        net_for_sfv = net.copy()
        visualize(nav, net_for_sfv, alg, data, mutations, targets)
        
        str_mutations = ','.join(mutations)
        str_targets = ''.join(['%s(%d)'%(tgt, val_inh) for tgt in targets])
        fname = "mt_[%s]_pert_[%s].jpg"%(str_mutations, str_targets)
        fpath_img = os.path.join(dpath, fname)
        print("[Image #%d] %s"%(i+1, fpath_img))
        write_image(net_for_sfv,
                    fpath_img,
                    scale_width=800, scale_height=800,
                    dpi_width=600, dpi_height=600,)
