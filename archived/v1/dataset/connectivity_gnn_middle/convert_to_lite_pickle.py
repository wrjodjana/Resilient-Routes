import pickle
import numpy as np

import os

data = os.listdir('data')

for data_file in data:
    with open(f'./data/{data_file}/all_result.pickle', 'rb') as handle:
        all_result = pickle.load(handle)

    # print(all_result[0]['node_res'])

    avg_prob_list = []
    for graph_idx in all_result.keys():
        avg_prob_list.append(np.mean(all_result[graph_idx]['node_res']).item())

    # print(avg_prob_list)
    # print("len(avg_prob_list): ", len(avg_prob_list))


    sort_graph_idx = np.argsort(avg_prob_list)
    # print("sort the list: ", sort_graph_idx)

    # print("major earthquake grpah idx: ", sort_graph_idx[0])
    # print("moderate earthquake grpah idx: ", sort_graph_idx[int(len(sort_graph_idx)/2)])
    # print("minor earthquake grpah idx: ", sort_graph_idx[-1])

    major_idx = sort_graph_idx[0]
    moderate_idx = sort_graph_idx[int(len(sort_graph_idx)/2)]
    minor_idx = sort_graph_idx[-1]

    all_result_lite = {
        'major': all_result[major_idx],
        'moderate': all_result[moderate_idx],
        'minor': all_result[minor_idx]
    }

    with open(f'./data/{data_file}/all_result_lite.pickle', 'wb') as handle:
        pickle.dump(all_result_lite, handle, protocol=pickle.HIGHEST_PROTOCOL)

