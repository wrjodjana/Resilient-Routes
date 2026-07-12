import pickle
import numpy as np

################################################################################
with open('./data_0.pickle', 'rb') as handle:
    graph_info = pickle.load(handle)

# dict_keys(['ratio', 'flow', 'capacity', 't0', 'demand_matrix', 'ca_list', 'od_list', 'T'])

# visualize on the edge:
# ratio
# flow
# capacity

# visualize on the node:
# demand_matrix
print(graph_info)
print(graph_info.keys())

