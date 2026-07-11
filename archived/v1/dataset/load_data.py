import pickle
import numpy as np

################################################################################
with open('./graph_info.pickle', 'rb') as handle:
    graph_info = pickle.load(handle)

# n_node
# n_bridge: will damage
# n_road: won't damage at all
# n_edge: n_road + n_bridge
# bridge_list
# road_list
# edge_list: bridge_list + road_list
print(graph_info)

################################################################################
with open('./all_result.pickle', 'rb') as handle:
    graph_data_all = pickle.load(handle)
    
# inlucde 200 scenarios
idx = 0
print(len(graph_data_all))
print(graph_data_all[idx].keys())

graph_data = graph_data_all[idx]

### node level connectivity
print(graph_data['node_res'].squeeze().shape)
print(graph_data['node_res'].squeeze()) # values between 0 to 1

### link connectivity probability
print(graph_data['edge_feat'].squeeze().shape)
print(graph_data['edge_feat'].squeeze()) # include every edge feature


################################################################################
SpreadSheet = np.genfromtxt('bridge_info_v2.csv', delimiter=',', dtype=None, encoding='utf-8-sig')
colNames = SpreadSheet[0, :]
Data = SpreadSheet[1:, :]

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


################################################################################
SpreadSheet = np.genfromtxt('map.csv', delimiter=',', dtype=None, encoding='utf-8-sig')
colNames = SpreadSheet[0, :]
node_file = SpreadSheet[1:, :]
id_list = node_file[:, np.where(colNames == 'id')[0][0]].astype(np.int32)
lat_list = node_file[:, np.where(colNames == 'lat')[0][0]].astype(np.float32)
lon_list = node_file[:, np.where(colNames == 'lon')[0][0]].astype(np.float32)
print(node_file)


