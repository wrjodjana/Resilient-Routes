import pickle
import numpy as np

with open('data/data_1_v2/all_result.pickle', 'rb') as handle:
    all_result = pickle.load(handle)
    
# print(all_result[0]['node_res'])

avg_prob_list = []
for graph_idx in all_result.keys():
    avg_prob_list.append(np.mean(all_result[graph_idx]['node_res']).item())

print(avg_prob_list)
print("len(avg_prob_list): ", len(avg_prob_list))


sort_graph_idx = np.argsort(avg_prob_list)
print("sort the list: ", sort_graph_idx)

print("major earthquake grpah idx: ", sort_graph_idx[0])
print("moderate earthquake grpah idx: ", sort_graph_idx[int(len(sort_graph_idx)/2)])
print("minor earthquake grpah idx: ", sort_graph_idx[-1])
# ... existing code ...

# Print the sorted average probabilities
print("Sorted average probabilities: ", [avg_prob_list[i] for i in sort_graph_idx])

# Get all probabilities for major, moderate, and minor earthquakes
major_earthquake_probs = [all_result[idx]['node_res'] for idx in sort_graph_idx[:1]]
moderate_earthquake_probs = [all_result[idx]['node_res'] for idx in sort_graph_idx[len(sort_graph_idx)//2:len(sort_graph_idx)//2+1]]
minor_earthquake_probs = [all_result[idx]['node_res'] for idx in sort_graph_idx[-1:]]

print("Major earthquake probabilities: ", major_earthquake_probs)
print("Moderate earthquake probabilities: ", moderate_earthquake_probs)
print("Minor earthquake probabilities: ", minor_earthquake_probs)