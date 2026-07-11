from utils_v4_dev import *
# run_simulation, save_pickle, plot_system, cal_bridge_info, load_data_case
import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
import pickle
import os
import time

# random.seed(246)
# np.random.seed(4812)

# prepare data
n_node = 103
n_bridge = 127
n_road = 32

dataset_name = 'data'
imageset_name = 'img'
for idx in range(0, 103):
    target_node_ID, node_thre, node_class, num_sample, N_iter, \
        data_dir, img_dir, bridge_list, road_list = load_data_case(idx, 200, dataset_name, imageset_name)

    # sanity check
    assert(len(road_list) == n_road)
    assert(len(bridge_list) == n_bridge)

    p_bridge_collapse_list = []
    p_connect_list = []

    if not os.path.exists(data_dir):    os.makedirs(data_dir)
    if not os.path.exists(img_dir):    os.makedirs(img_dir)

    plot_system(n_node, n_bridge, n_road, bridge_list, road_list, img_dir)
    
    t0 = time.time()

    all_graph_data_dict = {}
    
    for j in range(num_sample):
        p_road_collapse = np.zeros(n_road)

        # combine
        edge_num_all = (n_bridge, n_road)
        edge_all = (bridge_list, road_list)

        # run simulation, 
        p_connect, std_connect, p_bridge_collapse = run_simulation(n_node, \
            edge_num_all, edge_all, p_road_collapse, target_node_ID, N_iter)

        p_bridge_collapse_list.append(p_bridge_collapse)
        p_connect_list.append(p_connect)
        p_collapse_all = (p_bridge_collapse, p_road_collapse)

        # create each graph into pickle
        graph_data = save_pickle(n_node, edge_num_all, edge_all, \
            p_collapse_all, p_connect, target_node_ID, \
            (data_dir, img_dir), j, node_thre, node_class)
        all_graph_data_dict[j] = graph_data
        
        if j % 10 == 0:
            print('run {} graphs'.format(j))

    save_all_in_one_pickle(data_dir, img_dir, all_graph_data_dict)
    
    print("BFS time: ", time.time() - t0)

    # save general graph info 
    graph_info = dict()
    graph_info['n_node'] = n_node
    graph_info['n_bridge'] = n_bridge
    graph_info['n_road'] = n_road
    graph_info['n_edge'] = n_road + n_bridge
    graph_info['bridge_list'] = bridge_list
    graph_info['road_list'] = road_list
    graph_info['edge_list'] = bridge_list + road_list

    with open(data_dir+'/graph_info.pickle', 'wb') as handle:
        pickle.dump(graph_info, handle, protocol=pickle.HIGHEST_PROTOCOL)

    np.savetxt(data_dir+"/node_connect.txt", p_connect_list, fmt='%1.2f')
    np.savetxt(data_dir+"/bridge_collapse.txt", p_bridge_collapse_list, fmt='%1.4f')
