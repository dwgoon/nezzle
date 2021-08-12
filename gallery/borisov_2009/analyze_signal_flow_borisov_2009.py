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

from nezzle.fileio import write_image
from sfv import visualize_signal_flow

dpath = os.path.dirname(__file__)
fpath = os.path.join(dpath, 'borisov_2009_activity_label_pos.csv')


def visualize(nav, net, alg, data, mutations, targets):
    
    n2i = data.n2i
    N = len(n2i)
    
    
    #act, F = analyze_perturb(alg, data, ['RAS', 'GAB1'], get_trj=False)
    b = np.zeros((N,), dtype=np.float)
    
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
    
    # Mutation
    #b[n2i['RAS']] = 10    
    #W_pert[:, n2i['RAS']] *= 10
    
    for mut in mutations:
        b[n2i[mut]] = 1
        W_pert[n2i[mut], :] *= 0
        W_pert[:, n2i[mut]] *= 10
    
    alg.W = W_pert

    b[inds] = vals
    x_pert, trj_pert = alg.propagate_iterative(
                                W_pert, 
                                b,
                                b,
                                alg.params.alpha,
                                get_trj=False)

    act = x_pert - x_ctrl

    F = W_pert*x_pert - W_ctrl*x_ctrl

    
    font = QFont('Arial', 11)
    visualize_signal_flow(net,
                          F, act,
                          data.A,
                          data.n2i,
                          lw_min=1.5,
                          lw_max=5,
                          pct_link=90,
                          pct_act=90,
                          fix_act_label=False,
                          font=font)
        
    df_pos = pd.read_csv(fpath)

    for idx, row in df_pos.iterrows():
        label = net.labels[row.id]
        label.setX(row.x)
        label.setY(row.y)
        
    for iden, node in net.nodes.items():
        node['BORDER_WIDTH'] = 2
        node['BORDER_COLOR'] = QColor(40, 40, 40)  #Qt.black
        
    for iden, link in net.links.items():
        color = QColor(link['FILL_COLOR'])
        color.setAlpha(70)
        link['FILL_COLOR'] = color
    
    nav.append_item(net)


def update(nav, net):
    ds = sfa.DataSet()
    ds.create("BORISOV_2009")
    data = ds["BORISOV_2009"]["30m_AUC_EGF=1+I=100"]
    
    algs = sfa.AlgorithmSet()
    alg = algs.create("SP")

    alg.params.alpha = 0.5
    alg.params.apply_weight_norm = True
    alg.params.use_rel_change = True
    
    mutations = ['PI3K']
    list_targets = [['PIP3'], ['PDK1']]#[['GAB1'], ['IRS'], ['PDK1'], ['GS']] #[['RAS', 'PIP3'], ['MEK', 'PDK1']]
    #list_targets = [['SFK', 'GAB1'],] #, 'GAB1']
    val_inh = -10
    for targets in list_targets:
        data.df_ptb.loc[targets, 'Value'] = val_inh
        data.A[data.n2i['RAF'], data.n2i['AKT']] = 0
        alg.data = data        
        alg.initialize()

        net_for_img = net.copy()
        visualize(nav, net_for_img, alg, data, mutations, targets)
        
        str_mutations = ','.join(mutations)
        str_targets = ''.join(['%s(%d)'%(tgt, val_inh) for tgt in targets])
        fname = "mt_[%s]_pert_[%s].jpeg"%(str_mutations, str_targets)
        fpath_img = os.path.join(dpath, fname)
        print(fpath_img)
        write_image(net_for_img, fpath_img,
                    scale_width=800, scale_height=800,
                    dpi_width=600, dpi_height=600,)
