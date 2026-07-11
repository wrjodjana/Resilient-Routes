# from flask import *
# import pickle
# import json
# import numpy as np
# import pandas as pd
# from flask_cors import CORS
# import csv
# from collections import *
# import heapq
# import subprocess
# app = Flask(__name__)

# CORS(app)
# @app.route('/')
# def home():
#     return "Welcome to the Flask App!"

# ### CONVERT FROM DMS TO DECIMAL
# ``

# def dms_to_decimal(dms, is_latitude=True):
#     degrees = int(dms / 1000000) 
#     minutes = int((dms % 1000000) / 10000)
#     seconds = (dms % 10000) / 100.0
#     decimal_degrees = degrees + minutes / 60 + seconds / 3600
#     if not is_latitude:
#         decimal_degrees *= -1
#     return decimal_degrees

# ### GET BRIDGE COORDINATES

# @app.route('/data/bridge-info/<dataset>')
# def bridge_information(dataset):
#     bridge_csv_path = f'./{dataset}/bridges.csv'
#     SpreadSheet = np.genfromtxt(bridge_csv_path, delimiter=',', dtype=None, encoding='utf-8-sig')
#     colNames = SpreadSheet[0, :]
#     Data = SpreadSheet[1:, :]
#     print(Data)
    
#     latitude_indices = np.where(colNames == 'LAT_016')[0][0]
#     longitude_indices = np.where(colNames == 'LONG_017')[0][0]
    
#     latitude = np.array([dms_to_decimal(dms, is_latitude=True) for dms in Data[:, latitude_indices].astype(int)])
#     longitude = np.array([dms_to_decimal(dms, is_latitude=False) for dms in Data[:, longitude_indices].astype(int)])
#     coordinates = [{
#         "latitude": lat,
#         "longitude": lon
#     } for lat, lon in zip(latitude, longitude)]
    
#     return jsonify({"bridge_coordinates": coordinates})


# if __name__ == '__main__':
#     app.run(debug=True)

# ############################################ OLD MAP:


# # @app.route('/data/<dataset>')
# # def get_data(dataset):
# #     # Load graph information
# #     graph_info_path = f'./{dataset}/graph_info.pickle'
# #     with open(graph_info_path, 'rb') as handle:
# #         graph_info = pickle.load(handle)
    
# #     edge_list = graph_info.get('edge_list')
# #     # Load all results
# #     all_result_path = f'./{dataset}/all_result.pickle'
# #     with open(all_result_path, 'rb') as handle:
# #         graph_data_all = pickle.load(handle)
# #     idx = 0
# #     graph_data = graph_data_all[idx]
# #     # Load map information
# #     map_csv_path = f'./{dataset}/map.csv'
# #     SpreadSheet_map = np.genfromtxt(map_csv_path, delimiter=',', dtype=None, encoding='utf-8-sig')
# #     colNames_map = SpreadSheet_map[0, :]
# #     node_file = SpreadSheet_map[1:, :]
# #     id_list = [int(id) for id in node_file[:, np.where(colNames_map == 'id')[0][0]]]
# #     lat_list = [float(lat) for lat in node_file[:, np.where(colNames_map == 'lat')[0][0]]]
# #     lon_list = [float(lon) for lon in node_file[:, np.where(colNames_map == 'lon')[0][0]]]
# #     # Prepare data to send as JSON
# #     data = {
# #         "graph_info": graph_info,
# #         "edge_list": edge_list,
# #         "map_nodes": {
# #             "ids": id_list,
# #             "lats": lat_list,
# #             "lons": lon_list
# #         },
# #         "node_res": graph_data['node_res'].squeeze().tolist(),
# #         "edge_feat": graph_data['edge_feat'].squeeze().tolist()
# #     }
# #     return jsonify(data)
# # ####################################################
# # @app.route('/data/nodes/<dataset>')
# # def get_nodes_data(dataset):
# #     node1_id = request.args.get('node1', type=int)
# #     node2_id = request.args.get('node2', type=int)
# #     node1_data = fetch_node_data(node1_id, dataset)
# #     node2_data = fetch_node_data(node2_id, dataset)
# #     graph_info_path = f'./{dataset}/graph_info.pickle'
# #     with open(graph_info_path, 'rb') as handle:
# #         graph_info = pickle.load(handle)
# #     edge_list = graph_info.get('edge_list')
# #     graph = defaultdict(list)
# #     for start, end in edge_list:
# #         graph[start].append(end)
# #         graph[end].append(start)
# #     path = dijkstra(graph, node1_id, node2_id)
# #     data = {
# #         "node1": node1_data,
# #         "node2": node2_data,
# #         "path": path
# #     }
# #     return jsonify(data)

# # def fetch_node_data(node_id, dataset):
# #     csv_file_path = f'./{dataset}/map.csv'
# #     with open(csv_file_path, mode='r', encoding='utf-8-sig') as file:
# #         reader = csv.DictReader(file)
# #         for row in reader:
# #             if int(row['id']) == node_id:
# #                 return {
# #                     "node_id": node_id,
# #                     "latitude": float(row['lat']),
# #                     "longitude": float(row['lon'])
# #                 }
# #     return {"node_id": node_id, "error": "Node data not found"}

# # def dijkstra(graph, start, end):
# #     min_heap = [(0, start, [])]
# #     visited = set()
# #     while min_heap:
# #         (cost, vertex, path) = heapq.heappop(min_heap)
# #         if vertex not in visited:
# #             visited.add(vertex)
# #             path = path + [vertex]
# #             if vertex == end:
# #                 return path
# #             for next_vertex in graph[vertex]:
# #                 if next_vertex not in visited:
# #                     heapq.heappush(min_heap, (cost + 1, next_vertex, path))
# #     return []
# # ################################################
# # @app.route('/data/bridges/<dataset>')
# # def get_bridges_data(dataset):
# #     # Load bridge information
# #     bridge_csv_path = f'./{dataset}/bridge_info.csv'
# #     SpreadSheet = np.genfromtxt(bridge_csv_path, delimiter=',', dtype=None, encoding='utf-8-sig')
# #     colNames = SpreadSheet[0, :]
# #     Data = SpreadSheet[1:, :]
# #     # Load other bridge information
# #     bridge_id = Data[:, np.where(colNames == 'structure member')[0][0]]
# #     year_built = Data[:, np.where(colNames == 'year_built_027')[0][0]]
# #     total_length = Data[:, np.where(colNames == 'structure_len_mt_049')[0][0]]
# #     def dms_to_decimal(dms, is_latitude=True):
# #         degrees = int(dms / 1000000) 
# #         minutes = int((dms % 1000000) / 10000)
# #         seconds = (dms % 10000) / 100.0
# #         decimal_degrees = degrees + minutes / 60 + seconds / 3600
# #         if not is_latitude:
# #             decimal_degrees *= -1
# #         return decimal_degrees
    
# #     latitude_indices = np.where(colNames == 'lat_016')[0][0]
# #     longitude_indices = np.where(colNames == 'long_017')[0][0]
# #     latitude = np.array([dms_to_decimal(dms, is_latitude=True) for dms in Data[:, latitude_indices].astype(int)])
# #     longitude = np.array([dms_to_decimal(dms, is_latitude=False) for dms in Data[:, longitude_indices].astype(int)])
# #     bridge_info = [{
# #         "bridge_id": str(b_id),
# #         "year_built": int(y_b),
# #         "total_length": int(t_l),
# #         "latitude": lat,
# #         "longitude": lon
# #     } for  b_id, y_b, t_l, lat, lon in zip(
# #           bridge_id, year_built, total_length, latitude, longitude
# #     )]
# #     data = {
# #         "bridges": bridge_info,
# #     }
# #     return jsonify(data)

# # ################################################
# # @app.route('/data/matrix/<dataset>')
# # def get_matrix_data(dataset):
# #     node_csv = f'./{dataset}/modified_coord.csv'
# #     SpreadSheet_traffic = np.genfromtxt(node_csv, delimiter=',', dtype=None, encoding='utf-8-sig')
# #     colNames_traffic = SpreadSheet_traffic[0, :]
# #     node_file = SpreadSheet_traffic[1:, :]
# #     id_list = [int(id) for id in node_file[:, np.where(colNames_traffic == 'id')[0][0]]]
# #     lat_list = [float(lat) for lat in node_file[:, np.where(colNames_traffic == 'lat')[0][0]]]
# #     lon_list = [float(lon) for lon in node_file[:, np.where(colNames_traffic == 'lon')[0][0]]]
# #     matrix_path = f'./{dataset}/data_0.pickle'
# #     with open(matrix_path, 'rb') as handle:
# #         matrix_graph = pickle.load(handle)
# #     od_demand = matrix_graph.get('demand_matrix')
# #     print(od_demand.tolist())
# #     data = {
# #         "matrix": od_demand.tolist(),
# #         "map_nodes": {
# #             "ids": id_list,
# #             "lats": lat_list,
# #             "lons": lon_list
# #         },
# #     }
    
# #     return jsonify(data)

# # def convert_keys(data):
# #     new_data = {}
# #     for (start, end), value in data.items():
# #         # Increment both start and end node IDs and convert to string key
# #         new_key = f"{start + 1}-{end + 1}"
# #         new_data[new_key] = value
# #     return new_data

# # @app.route('/data/traffic/<dataset>')
# # def get_traffic_data(dataset):
# #     traffic_path = f'./{dataset}/data_0.pickle'
# #     with open(traffic_path, 'rb') as handle:
# #         traffic_graph = pickle.load(handle)
# #     ratio = convert_keys(traffic_graph.get('ratio', {}))    
# #     flow = convert_keys(traffic_graph.get('flow', {}))
# #     capacity = convert_keys(traffic_graph.get('capacity', {}))
    
# #     node_csv = f'./{dataset}/modified_coord.csv'
# #     SpreadSheet_traffic = np.genfromtxt(node_csv, delimiter=',', dtype=None, encoding='utf-8-sig')
# #     colNames_traffic = SpreadSheet_traffic[0, :]
# #     node_file = SpreadSheet_traffic[1:, :]
# #     id_list = [int(id) for id in node_file[:, np.where(colNames_traffic == 'id')[0][0]]]
# #     lat_list = [float(lat) for lat in node_file[:, np.where(colNames_traffic == 'lat')[0][0]]]
# #     lon_list = [float(lon) for lon in node_file[:, np.where(colNames_traffic == 'lon')[0][0]]]
# #     edge_csv = f'./{dataset}/Ca_list.csv'
# #     SpreadSheet_edges = np.genfromtxt(edge_csv, delimiter=',', dtype=None, encoding='utf-8-sig', names=True)
# #     edges = [{
# #         "init_node": int(row['init_node']),
# #         "term_node": int(row['term_node']),
# #         "capacity": float(row['capacity']),
# #         "length": float(row['length'])
# #     } for row in SpreadSheet_edges]
# #     data = {
# #         "ratio": ratio,
# #         "flow": flow,
# #         "capacity": capacity,
# #         "map_nodes": {
# #             "ids": id_list,
# #             "lats": lat_list,
# #             "lons": lon_list
# #         },
# #         "edges": edges
# #     }
# #     return jsonify(data)
# # ################################################
# # # first i need to get a user request like based on if they select minor, major or moderate earthquakes
# # # then based on that request, i would connect it to the bridge probability/link probability
# # # with this bridge probability/link probability i would run it on the neural network model
# # # the model will return information about node values and then visualise it


# # @app.route('/data/earthquake/<earthquake_type>/<target_node_id>/<dataset>')
# # def get_earthquake_data(earthquake_type, target_node_id, dataset):

# #     # load neural network model
# #     result = subprocess.run([
# #         'python', f'{dataset}/multitask_batch_test_only_reg_dev.py', 
# #         '--model_idx=7', '--dataset_name=data', '--imageset_name=img','--n_feat=4','--percentage=0.8','--batch_size=512', '--earthquake_type='+earthquake_type, '--target_node_id='+target_node_id
# #     ], capture_output=True, text=True)

# #     # Load graph information
# #     graph_info_path = f'./{dataset}/graph_info.pickle'
# #     with open(graph_info_path, 'rb') as handle:
# #         graph_info = pickle.load(handle)
    
# #     edge_list = graph_info.get('edge_list')
# #     # Load all results
# #     all_result_path = f'./{dataset}/all_result.pickle'
# #     with open(all_result_path, 'rb') as handle:
# #         graph_data_all = pickle.load(handle)
# #     idx = 0
# #     graph_data = graph_data_all[idx]
# #     # Load map information
# #     map_csv_path = f'./{dataset}/map.csv'
# #     SpreadSheet_map = np.genfromtxt(map_csv_path, delimiter=',', dtype=None, encoding='utf-8-sig')
# #     colNames_map = SpreadSheet_map[0, :]
# #     node_file = SpreadSheet_map[1:, :]
# #     id_list = [int(id) for id in node_file[:, np.where(colNames_map == 'id')[0][0]]]
# #     lat_list = [float(lat) for lat in node_file[:, np.where(colNames_map == 'lat')[0][0]]]
# #     lon_list = [float(lon) for lon in node_file[:, np.where(colNames_map == 'lon')[0][0]]]
    
# #     output_str = result.stdout.strip().split('\n')
# #     print(output_str)
# #     edge_probabilities = json.loads(output_str[0])
# #     node_probabilities = json.loads(output_str[1])
    

# #     data = {
# #         "graph_info": graph_info,
# #         "edge_list": edge_list,
# #         "map_nodes": {
# #             "ids": id_list,
# #             "lats": lat_list,
# #             "lons": lon_list
# #         },
# #         "edge_probabilities": edge_probabilities,
# #         "node_probabilities": node_probabilities
# #     }
    
# #     return jsonify(data)


# # @app.route('/data/traffic-earthquake/<earthquake_type>/<dataset>')
# # def get_traffic_earthquake(earthquake_type, dataset):
# #     result = subprocess.run([
# #         'python', 'sta_dataset/kfold_hetero_adaptive.py',
# #         '--map_name=' + dataset,
# #         '--model_idx=16',
# #         '--train_data_dir_list', f'data_{dataset}_major_00', f'data_{dataset}_minor_00', f'data_{dataset}_moderate_00',
# #         '--test_data_dir_list', f'data_{dataset}_{earthquake_type}_00',
# #         '--train_num_sample_list', '1', '1', '1', 
# #         '--test_num_sample_list', '1', 
# #         '--batch_size=1',
# #         '--gpu=-1'
# #     ], capture_output=True, text=True)

# #     node_csv = f'./sta_dataset/{dataset}/modified_coord.csv'
# #     SpreadSheet_traffic = np.genfromtxt(node_csv, delimiter=',', dtype=None, encoding='utf-8-sig')
# #     colNames_traffic = SpreadSheet_traffic[0, :]
# #     node_file = SpreadSheet_traffic[1:, :]
# #     id_list = [int(id) for id in node_file[:, np.where(colNames_traffic == 'id')[0][0]]]
# #     lat_list = [float(lat) for lat in node_file[:, np.where(colNames_traffic == 'lat')[0][0]]]
# #     lon_list = [float(lon) for lon in node_file[:, np.where(colNames_traffic == 'lon')[0][0]]]
    
# #     output_str = result.stdout.strip().split('\n')
# #     ratio_probabilities = json.loads(output_str[0])
# #     flow_probabilities = json.loads(output_str[1])

# #     traffic_path = f'./sta_dataset/{dataset}/data_0.pickle'
# #     with open(traffic_path, 'rb') as handle:
# #         traffic_graph = pickle.load(handle)
# #     ratio = convert_keys(traffic_graph.get('ratio', {}))    
# #     flow = convert_keys(traffic_graph.get('flow', {}))

# #     data = {
# #         "map_nodes": {
# #             "ids": id_list,
# #             "lats": lat_list,
# #             "lons": lon_list
# #         },
# #         "ratio": ratio,
# #         "flow": flow,
# #         "ratio_probabilities": ratio_probabilities,
# #         "flow_probabilities": flow_probabilities
# #     }
# #     return jsonify(data)
