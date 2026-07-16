from math import ceil

import random
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pickle
import scipy.stats
from scipy.stats import norm, truncexpon
import contextlib
import torch
from sklearn.utils.class_weight import compute_class_weight

### change magnitude: cal_bridge_info
### change feature "data" or "data_large": save_pickle
### dont save figure after MC: create_plot_regression
np.set_printoptions(linewidth=200)

NORM_DIST = 5.0
ALLOW_AFTER_PLOT = False
ALLOW_REG_PLOT = False
PERCENTAGE_LEFT = 0.4

def run_simulation(node_num, edge_num, edge_list, p_road_collapse, target_node, N_iter):
    
    n_node = node_num
    n_bridge, n_road = edge_num
    bridge_list, road_list = edge_list
    
    # duplicate bridge list
    bridge_edge, series_id, prob_survive, prob_failure = cal_bridge_info()

    # to do: compute prob for each edge
    # new feature: consider the series and parallel bridge
    p_bridge_survive = np.ones(n_bridge)
    start = 0
    for idx, edge in enumerate(bridge_list):
        # all bridge start with series_id = 0
        survive_prob_list = []
        series_list = []
        while start < len(bridge_edge) and edge == bridge_edge[start]:
            # compare
            p = prob_survive[start]
            curr_id = series_id[start]
            survive_prob_list.append(p)
            series_list.append(curr_id)
            start += 1
        p_bridge_survive[idx] = cal_edge_survive_prob(survive_prob_list, series_list)
    p_bridge_collapse = 1.0 - p_bridge_survive

    node_ID = [i for i in range(n_node)]
    bridge_ID = [i for i in range(n_bridge)]
    road_ID = [i for i in range(n_road)]

    edge_labels = dict(zip(bridge_list, p_bridge_collapse.round(2)))
    edge_labels.update(dict(zip(road_list, [1-i for i \
        in p_road_collapse.round(2)])))

    res = []
    for i in range(N_iter):
        # compute which bridge will not collapse
        p_bridge_sample = np.random.uniform(0.0, 1.0, size = n_bridge)
        survive = p_bridge_sample > p_bridge_collapse
        bridge_survive_list = [bridge_list[bridge_ID[i]] \
            for i in bridge_ID if survive[i]]
        G = nx.Graph()
        G.add_nodes_from(node_ID)
        G.add_edges_from(bridge_survive_list)
        G.add_edges_from(road_list)

        connected_node = nx.algorithms.descendants(G, target_node)
        connected_node.add(target_node)
        connectivity = [i in connected_node for i in range(n_node)]
        res.append(np.array(connectivity, np.intc))
    res = np.vstack(res)
    res_mean = np.mean(res, axis=0)
    res_std = np.std(res, axis=0)
    # print(res_std.round(4))
    # print(res_mean.round(4))
    return res_mean, res_std, p_bridge_collapse

def run_simulation_from_link(n_node, edge_num_all, edge_all, \
    p_road_collapse, p_bridge_collapse, target_idx, N_iter):
    
    n_bridge, n_road = edge_num_all
    bridge_list, road_list = edge_all
    node_ID = [i for i in range(n_node)]
    bridge_ID = [i for i in range(n_bridge)]
    road_ID = [i for i in range(n_road)]

    res = []
    for i in range(N_iter):
        # compute which bridge will not collapse
        p_edge_sample = np.random.uniform(0.0, 1.0, size = n_bridge)

        survive = p_edge_sample > p_bridge_collapse
        bridge_survive_list = [bridge_list[bridge_ID[i]] \
            for i in bridge_ID if survive[i]]
        G = nx.Graph()
        G.add_nodes_from(node_ID)
        G.add_edges_from(bridge_survive_list)
        G.add_edges_from(road_list)

        connected_node = nx.algorithms.descendants(G, target_idx)
        connected_node.add(target_idx)
        connectivity = [i in connected_node for i in range(n_node)]
        res.append(np.array(connectivity, np.intc))
    res = np.vstack(res)
    res_mean = np.mean(res, axis=0)
    res_std = np.std(res, axis=0)
    # print(res_std.round(4))
    # print(res_mean.round(4))
    return res_mean, res_std

# modify
def save_pickle(node_num, edge_num, edge_list, p_collapse_list, \
    p_connect, target_node, dir_list, idx, node_thre, node_class):
    n_node = node_num
    n_bridge, n_road = edge_num
    bridge_list, road_list = edge_list
    p_bridge_collapse, p_road_collapse = p_collapse_list
    data_dir, img_dir = dir_list

    node_ID = [i for i in range(n_node)]
    bridge_ID = [i for i in range(n_bridge)]
    road_ID = [i for i in range(n_road)]

    edge_labels = dict(zip(bridge_list, p_bridge_collapse.round(2)))
    edge_labels.update(dict(zip(road_list, p_road_collapse.round(2))))

    G = nx.Graph()
    G.add_nodes_from(node_ID)

    edge_list = bridge_list + road_list
    p_edge_collapse = np.concatenate((p_bridge_collapse, p_road_collapse), 0)
    weighted_edge_tuple = [(u, v, w.round(2)) for (u,v), w in zip(edge_list, p_edge_collapse)]
    weighted_edge_list = [[u, v, w.round(2)] for (u,v), w in zip(edge_list, p_edge_collapse)]
    weighted_edge_list = np.vstack(weighted_edge_list)
    G.add_weighted_edges_from(weighted_edge_tuple)
    
    # # for each graph, create a dataset, save in pickle file
    # # for 'data' dataset
    node_feat, edge_feat, node_res = [], [], []
    # # degree, max, min, #hop
    for node_id in range(n_node):
        n_feat = [G.degree[node_id], max([G.get_edge_data(*i)['weight'] for i in G.edges(node_id)]), \
            min([G.get_edge_data(*i)['weight'] for i in G.edges(node_id)]), \
                nx.shortest_path_length(G, node_id, target_node)]
        node_feat.append(n_feat)

    # # for 'data_large' dataset
    # # feature list: #hop, degree, [0%, 25%, 50%, 75%, 100%] percentile of edge weight of node,
    # # [0%, 25%, 50%, 75%, 100%] percentile of edge weight of node after considering the neighbour node
    # node_feat, edge_feat, node_res = [], [], []
    # for node_id in range(n_node):
    #     nei = G.neighbors(node_id)
    #     nei_weight = [np.max([G.get_edge_data(*i)['weight'] for i in G.edges(nei_node_id)]).tolist() for nei_node_id in nei]
    #     nei = G.neighbors(node_id)
    #     nei_edge = [G.get_edge_data(*(node_id, nei_node_id))['weight'] for nei_node_id in nei]
    #     nei_data = [u*v for u, v in zip(nei_weight, nei_edge)]
    #     n_feat = [nx.shortest_path_length(G, node_id, target_node), \
    #         G.degree[node_id], \
    #         np.quantile([G.get_edge_data(*i)['weight'] for i in G.edges(node_id)], 0.0), \
    #         np.quantile([G.get_edge_data(*i)['weight'] for i in G.edges(node_id)], 0.25), \
    #         np.quantile([G.get_edge_data(*i)['weight'] for i in G.edges(node_id)], 0.5), \
    #         np.quantile([G.get_edge_data(*i)['weight'] for i in G.edges(node_id)], 0.75), \
    #         np.quantile([G.get_edge_data(*i)['weight'] for i in G.edges(node_id)], 1.0),
    #         np.quantile(nei_data, 0.0), \
    #         np.quantile(nei_data, 0.25), \
    #         np.quantile(nei_data, 0.5), \
    #         np.quantile(nei_data, 0.75), \
    #         np.quantile(nei_data, 1.0)]
    #     node_feat.append(n_feat)

    graph_data = dict()
    graph_data['n_node'] = n_node
    graph_data['node_order'] = [i for i in range(n_node)]
    graph_data['node_feat'] =  np.vstack(node_feat) # n_node x 4, [#edge, max prob, min prob, min #edge to dist]
    graph_data['node_res'] =  p_connect.reshape(-1, 1) # n_node x 1
    graph_data['node_thre'] = node_thre
    graph_data['node_class'] =  np.zeros_like(p_connect.reshape(-1, 1), dtype=np.intc)
    for class_id, thre in enumerate(graph_data['node_thre']):
        graph_data['node_class'][graph_data['node_res'] > thre] = class_id+1
    graph_data['edge_order'] =  weighted_edge_list[:, :2] # n_edge x 2
    graph_data['edge_feat'] =  weighted_edge_list[:, 2:] # n_edge x 1
    
    return graph_data
    
    # with open(data_dir+'/graph_{}.pickle'.format(idx), 'wb') as handle:
    #     pickle.dump(graph_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # if 0:
    #     G = nx.Graph()
    #     G.add_nodes_from(node_ID)
    #     G.add_edges_from(bridge_list)
    #     G.add_edges_from(road_list)

    #     plt.figure(figsize=(16,12))
    #     # pos = nx.spring_layout(G, seed = 100)
    #     pos = nx.kamada_kawai_layout(G)
    #     nx.draw(G, pos, cmap=plt.cm.Blues, with_labels=True, node_size=800, \
    #         font_color='red', font_weight='bold')
    #     nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red',font_size=10)
    #     plt.savefig(img_dir+"/path_{}.png".format(idx))

    #     # build graph after earthquake
    #     plt.figure(figsize=(16,12))
    #     val_map = {0: 1.0, 1: 0.5, 2: 0.0}
    #     values = [val_map.get(graph_data['node_class'].squeeze()[node], 0.25) for node in G.nodes()]
    #     nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red',font_size=10)
    #     nx.draw(G, pos, cmap=plt.get_cmap('viridis'), node_color=values, \
    #         with_labels=True, node_size=800, font_color='red', font_weight='bold')
    #     plt.savefig(img_dir+"/path_cla_after_{}.png".format(idx))
    #     plt.close('all')

    #     # build the regression graph after earthquake
    #     plt.figure(figsize=(16,12))
    #     nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red',font_size=10)
    #     nx.draw(G, pos, cmap=plt.cm.Blues, node_color=graph_data['node_res'].squeeze(), \
    #         with_labels=True, node_size=800, font_color='red', font_weight='bold')
    #     sm = plt.cm.ScalarMappable(cmap=plt.cm.Blues, norm=plt.Normalize(vmin = 0.0, vmax=1.0))
    #     plt.colorbar(sm)
    #     plt.savefig(img_dir+"/path_reg_after_{}.png".format(idx))
    #     plt.close('all')

def save_all_in_one_pickle(data_dir, img_dir, all_graph_data_dict):
    with open('{}/all_result.pickle'.format(data_dir), 'wb') as handle:
        pickle.dump(all_graph_data_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

def create_plot(prediction, data_dir, img_dir, img_idx):
    with open(data_dir+'/graph_info.pickle', 'rb') as handle:
        graph_info = pickle.load(handle)
    n_node = graph_info['n_node']
    n_bridge = graph_info['n_bridge']
    n_road = graph_info['n_road']
    edge_list = graph_info['edge_list']

    node_ID = [i for i in range(n_node)]
    bridge_ID = [i for i in range(n_bridge)]
    road_ID = [i for i in range(n_road)]

    G = nx.Graph()
    G.add_nodes_from(node_ID)
    G.add_edges_from(edge_list)

    # build graph after earthquake
    plt.figure()
    # pos = nx.spring_layout(G)
    pos = nx.kamada_kawai_layout(G)
    val_map = {0: 1.0, 1: 0.5, 2: 0.0}
    values = [val_map.get(prediction.squeeze()[node], 0.25) for node in G.nodes()]
    nx.draw(G, pos, node_size=800, cmap=plt.get_cmap('viridis'), node_color=values, \
        with_labels=True, font_color='white', font_weight='bold')
    plt.savefig(img_dir+"/path_prediction_{}.png".format(img_idx))
    plt.close('all')

def create_plot_all(prediction, prediction_cla, gt_cla, data_dir, img_dir, img_idx, num_class):
    with open(data_dir+'/graph_info.pickle', 'rb') as handle:
        graph_info = pickle.load(handle)
    with open(data_dir+'/graph_{}.pickle'.format(img_idx), 'rb') as handle:
        graph_data = pickle.load(handle)
    n_node = graph_info['n_node']
    n_bridge = graph_info['n_bridge']
    n_road = graph_info['n_road']
    edge_list = graph_info['edge_list']
    edge_order = graph_data['edge_order']
    edge_feat = graph_data['edge_feat']
    ground_truth = graph_data['node_res']

    node_ID = [i for i in range(n_node)]
    bridge_ID = [i for i in range(n_bridge)]
    road_ID = [i for i in range(n_road)]
    edge_labels = dict(zip(edge_list, edge_feat.round(2).tolist()))

    if 0:
        plot_reg_graph(img_dir, img_idx, edge_list, ground_truth, \
            node_ID, edge_labels, plt.Normalize(vmin = 0.0, vmax=1.0), "before")
        plot_reg_graph(img_dir, img_idx, edge_list, prediction, \
            node_ID, edge_labels, plt.Normalize(vmin = 0.0, vmax=1.0), "after")
        plot_reg_graph(img_dir, img_idx, edge_list, np.abs(prediction - ground_truth), \
            node_ID, edge_labels, plt.Normalize(vmin = 0.0, vmax=0.1), "diff")
    if 1:
        # G = nx.Graph()
        # G.add_nodes_from(node_ID)
        # G.add_edges_from(edge_list)
        # val_map = {0: 0.0, 1: 0.5, 2: 1.0}
        # values_before = [val_map.get(graph_data['node_class'].squeeze()[node], 0.25) for node in G.nodes()]
        plot_cla_graph(img_dir, img_idx, graph_data, edge_list, node_ID, edge_labels, 'before', gt_cla/(num_class-1), num_class)

        plot_cla_graph(img_dir, img_idx, graph_data, edge_list, node_ID, edge_labels, 'after', prediction_cla/(num_class-1), num_class)

def plot_cla_graph(img_dir, img_idx, graph_data, edge_list, node_ID, edge_labels, img_name, values, num_class):
    import matplotlib.pylab as pylab
    params = {"text.usetex": False,
            'font.size': 16,
            'figure.figsize': [10, 10/4*3]}
    pylab.rcParams.update(params)
    plt.rcParams['figure.dpi'] = 500

    # # build graph after earthquake
    G = nx.Graph()
    G.add_nodes_from(node_ID)
    G.add_edges_from(edge_list)

    temp = dict()
    for k, v in edge_labels.items():
        temp[k] = v[0]

    plt.figure()
    pos = nx.spring_layout(G, seed = 100)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=temp, font_color='red',font_size=12)
    nx.draw(G, pos, cmap=plt.get_cmap('viridis'), node_color=values, \
            with_labels=True, node_size=600, font_color='black', font_weight='bold', alpha=1.0, vmin=0.0, vmax=1.0)
    plt.tight_layout()
    plt.subplots_adjust(top=1.0, bottom=0.0, right=1.0, left=0.0, hspace=0, wspace=0)
    plt.savefig(img_dir+"/path_cla_{}_{}.png".format(img_name, img_idx))
    
    plt.close('all')

def plot_reg_graph(img_dir, img_idx, edge_list, values, node_ID, edge_labels, plot_norm, img_name):
    import matplotlib.pylab as pylab
    params = {"text.usetex": False,
            'font.size': 16,
            'figure.figsize': [10, 10/4*3]}
    pylab.rcParams.update(params)
    plt.rcParams['figure.dpi'] = 500

    # # build graph after earthquake
    G = nx.Graph()
    G.add_nodes_from(node_ID)
    G.add_edges_from(edge_list)

    temp = dict()
    for k, v in edge_labels.items():
        temp[k] = v[0]
    fig1 = plt.figure()
    pos = nx.spring_layout(G, seed = 100)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=temp, font_color='red',font_size=12)
    nx.draw(G, pos, cmap=plt.cm.Greens, node_color=values, \
            with_labels=True, node_size=600, font_color='red', font_weight='bold', width=2, vmin=plot_norm.vmin, vmax=plot_norm.vmax)
    sm = plt.cm.ScalarMappable(cmap=plt.cm.Greens, norm=plot_norm)
    position=fig1.add_axes([0.9,0.05,0.04,0.5])
    plt.colorbar(sm, cax=position)
    plt.tight_layout()
    plt.subplots_adjust(top=1.0, bottom=0.0, right=1.0, left=0.0, hspace=0, wspace=0)
    plt.savefig(img_dir+"/path_reg_{}_{}.jpg".format(img_name, img_idx))
    plt.close('all')

def create_plot_regression(prediction, data_dir, img_dir, img_idx):
    with open(data_dir+'/graph_info.pickle', 'rb') as handle:
        graph_info = pickle.load(handle)
    with open(data_dir+'/graph_{}.pickle'.format(img_idx), 'rb') as handle:
        graph_data = pickle.load(handle)
    n_node = graph_info['n_node']
    n_bridge = graph_info['n_bridge']
    n_road = graph_info['n_road']
    edge_list = graph_info['edge_list']
    edge_order = graph_data['edge_order']
    edge_feat = graph_data['edge_feat']
    ground_truth = graph_data['node_res']

    node_ID = [i for i in range(n_node)]
    bridge_ID = [i for i in range(n_bridge)]
    road_ID = [i for i in range(n_road)]
    edge_labels = dict(zip(edge_list, edge_feat.round(2).tolist()))

    # build graph after earthquake
    G = nx.Graph()
    G.add_nodes_from(node_ID)
    G.add_edges_from(edge_list)
    
    plt.figure(figsize=(16,12))
    # pos = nx.spring_layout(G, seed = 100)
    pos = nx.kamada_kawai_layout(G)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red',font_size=10)
    nx.draw(G, pos, cmap=plt.cm.Blues, node_color=prediction, \
        with_labels=True, node_size=800, font_color='red', font_weight='bold')
    sm = plt.cm.ScalarMappable(cmap=plt.cm.Blues, norm=plt.Normalize(vmin = 0.0, vmax=1.0))
    plt.colorbar(sm)
    plt.savefig(img_dir+"/path_reg_after_{}.png".format(img_idx))

    # plot the difference between prediction and the actual
    G = nx.Graph()
    G.add_nodes_from(node_ID)
    G.add_edges_from(edge_list)
    
    plt.figure(figsize=(16,12))
    # pos = nx.spring_layout(G, seed = 100)
    pos = nx.kamada_kawai_layout(G)
    # print(prediction.T)
    # print(ground_truth.T)
    # print(np.abs(prediction - ground_truth).T)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red',font_size=10)
    nx.draw(G, pos, cmap=plt.cm.Blues, node_color=np.abs(prediction - ground_truth), \
        with_labels=True, node_size=800, font_color='red', font_weight='bold', vmin=0,vmax=0.1)
    sm = plt.cm.ScalarMappable(cmap=plt.cm.Blues, norm=plt.Normalize(vmin = 0, vmax=0.1))
    plt.colorbar(sm)
    plt.savefig(img_dir+"/path_reg_diff_{}.png".format(img_idx))
    plt.close('all')

def plot_system(n_node, n_bridge, n_road, bridge_list, road_list, img_dir):
    
    node_ID = [i for i in range(n_node)]
    bridge_ID = [i for i in range(n_bridge)]
    road_ID = [i for i in range(n_road)]

    G = nx.Graph()
    G.add_nodes_from(node_ID)
    G.add_edges_from(bridge_list)
    G.add_edges_from(road_list)

    # build graph after earthquake
    plt.figure(figsize=(16, 12))
    #fixed_positions = {83:(-10, 10), 59:(10, 10), 38:(10, -10), 37:(-10, -10)}
    #fixed_nodes = fixed_positions.keys()
    #pos = nx.spring_layout(G, pos=fixed_positions, fixed = fixed_nodes)
    #pos = nx.spring_layout(G, seed = 100)
    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, pos, cmap=plt.cm.Blues, with_labels=True, node_size=800, font_color='red', font_weight='bold')
    plt.savefig(img_dir+"/graph_overview.png")
    plt.close('all')

def cal_bridge_info():
    SpreadSheet = np.genfromtxt('bridge_info_v3.csv', delimiter=',', dtype=None, encoding='utf-8-sig')
    colNames = SpreadSheet[0, :]
    Data = SpreadSheet[1:, :]

    # step -1: generated a random Magnitute from [6.5, 8.0]
    M = 8.0 - truncexpon.rvs(1.2)
    # M = 7.0

    # step 0: find the soil application factor
    G_03 = [0.25, 0.5, 0.75, 1.0, 1.25]
    G_10 = [0.1, 0.2, 0.3, 0.4, 0.5]
    A_03 = [1.6, 1.4, 1.2, 1.1, 1.0]
    A_10 = [2.4, 2.0, 1.8, 1.6, 1.5]

    # step 1: get bridge information
    node1 = Data[:, np.where(colNames == 'node1')[0][0]].astype(np.int32)
    node2 = Data[:, np.where(colNames == 'node2')[0][0]].astype(np.int32)
    edge = [(n1, n2) for n1, n2 in zip(node1, node2)]
    temp = list(set(edge))
    series_id = Data[:, np.where(colNames == 'serial class')[0][0]].astype(np.int32)
    bridge_class = Data[:, np.where(colNames == 'NBI class')[0][0]].astype(np.int32)
    bridge_id = Data[:, np.where(colNames == 'structure member')[0][0]]
    skew = Data[:, np.where(colNames == 'degrees_skew_034')[0][0]].astype(np.int32)
    num_span = Data[:, np.where(colNames == 'main_unit_spans_045')[0][0]].astype(np.int32)
    max_span_length = Data[:, np.where(colNames == 'max_span_len_mt_048')[0][0]].astype(np.int32)
    total_length = Data[:, np.where(colNames == 'structure_len_mt_049')[0][0]].astype(np.int32)

    # step 2,3 : compute PGA, Sa, modification factor K
    coeff_list = cal_fragility_coeff(bridge_class)
    medians, beta, K_3D_class, I_shape = coeff_list[:, 0:4], \
        coeff_list[:, 4], coeff_list[:, 5], coeff_list[:, 6]
    R, VS30, Bdepth, F, Q_0 = 31.37, 240.0, 0.75, 1.0, 150
    
    PGA, SA_03, SA_10 = cal_GK15(M, R, VS30, Bdepth, F, Q_0)
    SA_03, SA_10 = cal_Sa(SA_03, SA_10, G_03, G_10, A_03, A_10)
    
    skew[skew > 90] = 69
    K_skew = np.sqrt(np.sin((90.-skew)/180.*np.pi))
    K_shape = 2.5 * SA_10 / SA_03
    K_3D = cal_K_3D(K_3D_class, num_span)
    
    # step 4: compute modified fragility coefficient
    medians_modify = cal_modify_fragility_coeff(medians, K_skew, K_shape, K_3D, I_shape)

    # step 5: compute the failure prob of each bridge
    prob_failure = norm.cdf(np.log(SA_10/medians_modify[:, 2])/beta)
    prob_survive = 1 - prob_failure
    # plot_bridge_survive_prob(prob_survive)
    # print(norm.cdf(np.log(0.25/0.43)/beta))
    # print(norm.cdf(np.log(0.36/0.43)/beta))
    # print(norm.cdf(np.log(0.46/0.43)/beta))
    # print(norm.cdf(np.log(0.72/0.43)/beta))
    return edge, series_id, prob_survive, prob_failure

def cal_modify_fragility_coeff(medians, K_skews, K_shapes, K_3Ds, I_shapes):
    median_modify = medians.copy()
    for idx, (median, k_skew, k_3D, i_shape) in enumerate(zip(medians, K_skews, K_3Ds, I_shapes)):
        if i_shape == 0:
            slight_factor = 1
        elif i_shape == 1:
            slight_factor = min(1, K_shapes)
        else:
             raise RuntimeError('dont have i_shape value {}'.format(i_shape))
        median_modify[idx, 0] = median[0]*slight_factor
        median_modify[idx, 1] = median[1]*k_skew*k_3D
        median_modify[idx, 2] = median[2]*k_skew*k_3D
        median_modify[idx, 3] = median[3]*k_skew*k_3D
    return median_modify

def cal_fragility_coeff(bridge_classes):
    # return median, beta, K_3D_class, I_shape
    coeff_list = np.zeros((bridge_classes.shape[0], 7))
    for idx, bridge_class in enumerate(bridge_classes):
        # 6, 7, 8, 10, 11, 13, 15, 18, 19, 20, 21, 22, 23, 28
        if bridge_class == 1:
            coeff = [0.4, 0.5, 0.7, 0.9, 0.6, 1, 0]
        elif bridge_class == 2:
            coeff = [0.6, 0.9, 1.1, 1.7, 0.6, 1, 0]
        elif bridge_class == 3:
            coeff = [0.8, 1.0, 1.2, 1.7, 0.6, 1, 1]
        elif bridge_class == 4:
            coeff = [0.8, 1.0, 1.2, 1.7, 0.6, 1, 1]
        elif bridge_class == 5:
            coeff = [0.25, 0.35, 0.45, 0.7, 0.6, 1, 0]
        elif bridge_class == 6: 
            coeff = [0.3, 0.5, 0.6, 0.9, 0.6, 1, 0]
        elif bridge_class == 7: 
            coeff = [0.5, 0.8, 1.1, 1.7, 0.6, 1, 0]
        elif bridge_class == 8: 
            coeff = [0.35, 0.45, 0.55, 0.8, 0.6, 2, 0]
        elif bridge_class == 9: 
            coeff = [0.6, 0.9, 1.3, 1.6, 0.6, 3, 0]
        elif bridge_class == 10: 
            coeff = [0.6, 0.9, 1.1, 1.5, 0.6, 2, 1]
        elif bridge_class == 11: 
            coeff = [0.9, 0.9, 1.1, 1.5, 0.6, 3, 1]
        elif bridge_class == 13: 
            coeff = [0.3, 0.5, 0.6, 0.9, 0.6, 4, 0]
        elif bridge_class == 14: 
            coeff = [0.5, 0.8, 1.1, 1.7, 0.6, 1, 0]   
        elif bridge_class == 15: 
            coeff = [0.75, 0.75, 0.75, 1.1, 0.6, 5, 1]
        elif bridge_class == 18: 
            coeff = [0.3, 0.5, 0.6, 0.9, 0.6, 1, 0]
        elif bridge_class == 19: 
            coeff = [0.5, 0.8, 1.1, 1.7, 0.6, 1, 0]
        elif bridge_class == 20: 
            coeff = [0.35, 0.45, 0.55, 0.8, 0.6, 2, 0]
        elif bridge_class == 21: 
            coeff = [0.6, 0.9, 1.3, 1.6, 0.6, 3, 0]
        elif bridge_class == 22: 
            coeff = [0.6, 0.9, 1.1, 1.5, 0.6, 2, 1]
        elif bridge_class == 23: 
            coeff = [0.9, 0.9, 1.1, 1.5, 0.6, 3, 1]
        elif bridge_class == 28: 
            coeff = [0.8, 1.0, 1.2, 1.7, 0.6, 0, 0]
        else:
            raise RuntimeError('dont have bridge class {}'.format(bridge_class))
        coeff_list[idx, :] = coeff
    return coeff_list

# modify
def cal_GK15(M, R, VS30, Bdepth, F, Q_0, flag='m'):
    # M      = Moment magnitude
    # R      = Closest distance to fault rupture in km (i.e., Rrup)
    # VS30   = Average shear-wave velocity of the earth crust in the upper 30 m in m/s
    # Bdepth = Depth to 1,500 m/s shear-wave velocity (i.e., Z1.5)
    #         Bdepth = 0 for non-basin sites  (unit is km)
    # F      = Style of faulting
    #         F = 1.0 for strike-slip and normal faulting
    #         F = 1.28 for reverse faulting 
    #         F = 1.14 for combination of strike-slip and reverse
    #         faulting
    # Q_0    = Regional Q value (e.g., 150 for California)
    # flag   = 'm' for maximum horizontal randomly oriented component 
    #         'a' for average horizontal randomly oriented component
    amp = 1 if flag == 'm' else 1/1.12
    c1, c2, c3, c4, c5 = 0.14, -6.25, 0.37, 2.237, -7.542
    c6, c7, c8, c9, c10 = -0.125, 1.19, -6.15, 0.6, 0.345
    bv, VA = -0.24, 484.5
    m1, m2, m3, m4 = -0.0012, -0.38, 0.0006, 3.9
    a1, a2, a3 = 0.01686, 1.2695, 0.0001
    Dsp = 0.75
    t1, t2, t3, t4 = 0.001, 0.59, -0.0005, -2.3
    s1, s2, s3 = 0.001, 0.077, 0.3251

    # compute PGA
    G1 = np.log(( c1 * np.arctan(M + c2) + c3) * F)
    Ro = c4*M + c5
    Do = c6 * np.cos(c7 * (M + c8)) + c9
    G2 = -0.5 * np.log((1-R/Ro)**2 + 4 * (Do**2) * (R/Ro))
    G3 = -c10 * R / Q_0
    G4 = bv * np.log(VS30 / VA)
    A_Bdepth = 1.077/np.sqrt((1-(1.5/(Bdepth+0.1))**2)**2+4*0.7**2*(1.5/(Bdepth+0.1))**2)
    A_Bdist = 1/np.sqrt((1-(40/(R+0.1))**2)**2+4*0.7**2*(40/(R+0.1))**2)
    G5 = np.log(1 + A_Bdepth * A_Bdist)
    InPGA = G1 + G2 + G3 + G4 + G5
    PGA = np.exp(InPGA) * amp
    PGA = PGA*calculate_correlation(PGA) ## add spectral correlation assuming perfectly correlated

    # compute SA_03 and SA_10
    
    I = (a1*M+a2)*np.exp(a3*R)
    mu = m1*R + m2*M + m3*VS30 + m4
    S = s1*R - (s2*M + s3)
    Tsp_o = np.max([0.3, np.abs(t1*R + t2*M + t3*VS30 + t4)])
    zay = 1.763-0.25*np.arctan(1.4*(Bdepth-1))
    
    t = 0.3
    F1 = I*np.exp(-0.5*((np.log(t)+mu)/S)**2)
    F2 = 1/np.sqrt((1-(t/Tsp_o)**zay)**2 + 4*Dsp**2*(t/Tsp_o)**zay)
    Y = F1 + F2
    SA_03 = Y*np.exp(InPGA)*amp

    t = 1.0
    F1 = I*np.exp(-0.5*((np.log(t)+mu)/S)**2)
    F2 = 1/np.sqrt((1-(t/Tsp_o)**zay)**2 + 4*Dsp**2*(t/Tsp_o)**zay)
    Y = F1 + F2
    SA_10 = Y*np.exp(InPGA)*amp

    return PGA, SA_03, SA_10

def cal_K_3D(K_3D_classes, spans):
    # compute the K_3D for all the bridge
    K_3D = np.zeros_like(K_3D_classes)
    for idx, (K_3D_class, span) in enumerate(zip(K_3D_classes, spans)):
        if K_3D_class == 1:
            A, B = 0.25, 1.
        elif K_3D_class == 2:
            A, B = 0.33, 0.
        elif K_3D_class == 3:
            A, B = 0.33, 1.
        elif K_3D_class == 4:
            A, B = 0.09, 1.
        elif K_3D_class == 5:
            A, B = 0.05, 0.
        elif K_3D_class == 6:
            A, B = 0.2, 1.
        elif K_3D_class == 7:
            A, B = 0.1, 0.
        else:
            A, B = 0., 100.,
        res = span-B if span-B > 0.1 else 1.0
        K_3D[idx] = 1 + A/res
    return K_3D

def cal_Sa(SA_03, SA_10, G_03, G_10, A_03, A_10):
    # for A_03
    for idx, thre in enumerate(G_03):
        if SA_03 < thre:
            a_03 = A_03[idx]
            break
    # for A_10
    for idx, thre in enumerate(G_10):
        if SA_10 < thre:
            a_10 = A_10[idx]
            break
    return SA_03*a_03, SA_10*a_10

# add
def calculate_correlation(PGA):
    # T = 1.0
    # sigma1 = 0.668 + 0.0047 * np.log(T)
    # sigma2 = 0.8 + 0.13*np.log(T)
    # sigma = np.max([sigma1, sigma2])
    sigma = 0.660
    
    # SA_03_lb, SA_03_ub = SA_03/np.exp(sigma), SA_03*np.exp(sigma)
    # SA_10_lb, SA_10_ub = SA_10/np.exp(sigma), SA_10*np.exp(sigma)
    # print(SA_03, SA_03_lb, SA_03_ub)
    # print(SA_10, SA_10_lb, SA_10_ub)
    
    PGA_lb, PGA_ub = PGA/np.exp(sigma), PGA*np.exp(sigma)
    PGA_list = []
    with temp_seed(523):
        for i in range(100):
            PGA_sample = np.random.uniform(PGA_lb, PGA_ub)
            PGA_list.append(PGA_sample)
    
    espilon = np.mean(PGA_list) / PGA

    return espilon

def cal_edge_survive_prob(survive_prob_list, series_list):
    N = len(series_list)
    max_id = max(series_list)
    p_list = np.ones(max_id + 1)
    for target_id in range(max_id+1):
        for idx in np.where(np.array(series_list) == target_id)[0]:
            p_list[target_id] *= (1 - survive_prob_list[idx])
    prob = np.prod(1 - p_list)
    return prob

def load_data_case(idx, num_sample, dataset_name, imageset_name):
    bridge_list = [(0, 1), (0, 5), (0, 69), (1, 2), (1, 5), (2, 3), (3, 4), \
            (3, 7), (3,39), (4, 8), (4, 40), (5, 9), (5, 70), (6, 10), (6, 12), \
            (7, 8), (7, 10), (7, 15), (8, 16), (9, 18), (10, 11), (10, 13), \
            (11, 14), (11, 15), (12, 13), (12, 19), (14, 15), (14, 21), (14, 22), \
            (15, 17), (16, 17), (16, 23), (17, 22), (18, 19), (18, 26), (18, 62), \
            (19, 20), (20, 24), (20, 29), (21, 22), (21, 24), (22, 25), (23, 25), \
            (24, 25), (24, 27), (25, 28), (26, 33), (27, 29), (28, 30), (28, 31), \
            (30, 31), (31, 32), (31, 35), (32, 36), (33, 34), (34, 35), (35, 36), \
            (39, 41), (40, 42), (41, 42), (41, 46), (42, 43), (43, 61), (44, 45), \
            (46, 47), (47, 48), (47, 50), (47, 78), (48, 50), (48, 53), (49, 50), \
            (51, 54), (52, 56), (52, 82), (53, 54), (56, 58), (57, 58), (57, 59), (59, 60), \
            (60, 61), (62, 63), (62, 64), (63, 65), (64, 70), (65, 71), (66, 67), \
            (67, 68), (67, 73), (68, 69), (68, 79), (71, 72), (71, 74), (72, 73), \
            (73, 75), (74, 75), (74, 83), (75, 76), (75, 81), (76, 77), (76, 80), \
            (77, 78), (77, 79), (78, 79), (80, 81)]  
    road_list = [(1,6), (2,6), (9,12), (13,20), (13,21), (17,23), \
            (19,26), (23,32), (29,33), (30,34), (33,37), (36,38), \
            (43, 44), (44, 46), (45, 49), (50, 51), (49, 51), \
            (53, 56), (54, 55), (55, 56), (55, 57), (63, 64), (64, 66), \
            (65, 66), (66, 72), (67, 70), (69, 70), (81, 82), (82, 83)]
    # compatiable with bridge_info_v3
    target_node_ID = idx
    node_thre = [0.75]
    node_class = len(node_thre) + 1
    N_iter = 10000
    data_dir, img_dir = './{}/data_{}_v3'.format(dataset_name, target_node_ID), './{}/img_{}_v3'.format(imageset_name, target_node_ID) 

    bridge_list = sorted(bridge_list, key=lambda tup: (tup[0],tup[1]))
    road_list  = sorted(road_list, key=lambda tup: (tup[0],tup[1]))
    return (target_node_ID, node_thre, node_class, num_sample, N_iter, data_dir, img_dir, bridge_list, road_list)

def load_edge_list():
    n_node = 84
    n_bridge = 104
    n_road = 29
    bridge_list = [(0, 1), (0, 5), (0, 69), (1, 2), (1, 5), (2, 3), (3, 4), \
            (3, 7), (3,39), (4, 8), (4, 40), (5, 9), (5, 70), (6, 10), (6, 12), \
            (7, 8), (7, 10), (7, 15), (8, 16), (9, 18), (10, 11), (10, 13), \
            (11, 14), (11, 15), (12, 13), (12, 19), (14, 15), (14, 21), (14, 22), \
            (15, 17), (16, 17), (16, 23), (17, 22), (18, 19), (18, 26), (18, 62), \
            (19, 20), (20, 24), (20, 29), (21, 22), (21, 24), (22, 25), (23, 25), \
            (24, 25), (24, 27), (25, 28), (26, 33), (27, 29), (28, 30), (28, 31), \
            (30, 31), (31, 32), (31, 35), (32, 36), (33, 34), (34, 35), (35, 36), \
            (39, 41), (40, 42), (41, 42), (41, 46), (42, 43), (43, 61), (44, 45), \
            (46, 47), (47, 48), (47, 50), (47, 78), (48, 50), (48, 53), (49, 50), \
            (51, 54), (52, 56), (52, 82), (53, 54), (56, 58), (57, 58), (57, 59), (59, 60), \
            (60, 61), (62, 63), (62, 64), (63, 65), (64, 70), (65, 71), (66, 67), \
            (67, 68), (67, 73), (68, 69), (68, 79), (71, 72), (71, 74), (72, 73), \
            (73, 75), (74, 75), (74, 83), (75, 76), (75, 81), (76, 77), (76, 80), \
            (77, 78), (77, 79), (78, 79), (80, 81)]  
    
    road_list = [(1,6), (2,6), (9,12), (13,20), (13,21), (17,23), \
            (19,26), (23,32), (29,33), (30,34), (33,37), (36,38), \
            (43, 44), (44, 46), (45, 49), (50, 51), (49, 51), \
            (53, 56), (54, 55), (55, 56), (55, 57), (63, 64), (64, 66), \
            (65, 66), (66, 72), (67, 70), (69, 70), (81, 82), (82, 83)]
    
    bridge_list = sorted(bridge_list, key=lambda element: (element[0], element[1]))
    road_list = sorted(road_list, key=lambda element: (element[0], element[1]))
    
    return bridge_list, road_list, n_node, n_bridge, n_road

# def reserve_sample(bridge_list, road_list, n_node):
#     n_sample = ceil(PERCENTAGE_LEFT*n_node)
#     G = nx.Graph()
#     node_ID = [i for i in range(n_node)]
#     G.add_nodes_from(node_ID)
#     G.add_edges_from(bridge_list)
#     G.add_edges_from(road_list)
#     _, parts = metis.part_graph(G, n_sample, recursive=True)
#     reserve_targets = []
#     with temp_seed(114):
#         for idx in range(n_sample):
#             if np.where(np.array(parts) == idx)[0].shape[0] > 0:
#                 res = np.random.choice(np.where(np.array(parts) == idx)[0])
#                 reserve_targets.append(res)
#     return reserve_targets

# def generate_sample(bridge_list, road_list, n_node, n_bridge, n_road, percentage):
#     if percentage <= 1-PERCENTAGE_LEFT:
#         n_sample = ceil(percentage*n_node)
#         G = nx.Graph()
#         node_ID = [i for i in range(n_node)]
#         G.add_nodes_from(node_ID)
#         G.add_edges_from(bridge_list)
#         G.add_edges_from(road_list)
#         _, parts = metis.part_graph(G, n_sample, recursive=True)
#         sample_targets = []
#         with temp_seed(115):
#             for idx in range(n_sample):
#                 # print("partition {}".format(np.where(np.array(parts) == idx)[0]))
#                 if np.where(np.array(parts) == idx)[0].shape[0] > 0:
#                     res = np.random.choice(np.where(np.array(parts) == idx)[0])
#                     sample_targets.append(res)
#         # remove the node in reserve target
#         reserve_targets = reserve_sample(bridge_list, road_list, n_node)
#         print("reserve_targets", reserve_targets)
#         sample_targets = [sample_targets[idx] for idx in range(len(sample_targets)) if sample_targets[idx] not in reserve_targets]
#         # find remain target, and remaining number,
#         remain_targets = [i for i in range(n_node) if i not in reserve_targets and i not in sample_targets]
#         remain_num = n_sample - len(sample_targets)
        
#         if remain_num <= 0:
#             complementary_targets = []
#         else:
#             try:
#                 complementary_targets = random.sample(remain_targets, remain_num)
#             except:
#                 complementary_targets = remain_targets
#         sample_targets = sample_targets + complementary_targets
#     else:
#         sample_targets = [i for i in range(n_node)]
#     return sample_targets

def reserve_sample(bridge_list, road_list, n_node):
    n_sample = ceil(PERCENTAGE_LEFT*n_node)
    G = nx.Graph()
    node_ID = [i for i in range(n_node)]
    G.add_nodes_from(node_ID)
    G.add_edges_from(bridge_list)
    G.add_edges_from(road_list)
    
    with temp_seed(114):
        reserve_targets = np.random.choice(list(G.nodes()), size=n_sample, replace=False)

    return reserve_targets

def generate_sample(bridge_list, road_list, n_node, n_bridge, n_road, n_percentage, random=True):
    G = nx.Graph()
    node_ID = [i for i in range(n_node)]
    G.add_nodes_from(node_ID)
    G.add_edges_from(bridge_list)
    G.add_edges_from(road_list)
    with temp_seed(123):
        sample_targets = np.random.choice(list(G.nodes()), size=int(n_node*n_percentage), replace=False)
    return sample_targets

def plot_bridge_survive_prob(prob):
    plt.figure()
    plt.plot(prob)
    plt.xlabel('bridge ID')
    plt.ylabel('survive probability')
    plt.savefig('survive_probability.jpg')
    plt.close('all')

@contextlib.contextmanager
def temp_seed(seed):
    state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(state)

def cal_label_distribution(dataset, cla_num):
    all_class = []
    for data in dataset:
        all_class.append(data.ndata['class'].squeeze())
    all_class = torch.hstack(all_class).squeeze()
    all_class = all_class.cpu().detach().numpy()
    weights = compute_class_weight('balanced', np.arange(cla_num), all_class)
    
    return weights.tolist()
