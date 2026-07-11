import os
import numpy as np
import pickle
import time
from math import ceil
import matplotlib.pyplot as plt

from utils_v3_dev import load_edge_list, generate_sample, reserve_sample

import argparse

# np.random.seed(234) #234 523 42
np.set_printoptions(linewidth=400, precision=3)

device = 'cpu'
print("using device: {}".format(device))

class BridgeDataset():
    def __init__(self, num_sample, data_dir):
        self.num_sample = num_sample
        self.data_dir = data_dir
        
        self.all_X, self.all_Y_reg, self.all_Y_class = self.process()
        
    def process(self):
        all_X, all_Y_reg, all_Y_class = [], [], []
        num_sample_list = self.num_sample if type(self.num_sample) == list else [self.num_sample]
        data_dir_list = self.data_dir if type(self.num_sample) == list else [self.data_dir]
        for num_sample, dir in zip(num_sample_list, data_dir_list):

            # The label and number of nodes are values.
            graph_id_range = [i for i in range(num_sample)]
            
            with open(dir+'/all_result.pickle', 'rb') as handle:
                graph_data_all = pickle.load(handle)
                
            for graph_id in graph_id_range:
                # load each graph
                graph_data = graph_data_all[graph_id]
                feat = graph_data['edge_feat'].reshape(-1)
                
                all_X.append(feat)
                all_Y_reg.append(graph_data['node_res'].reshape(-1))
                all_Y_class.append(graph_data['node_class'].reshape(-1))
        
        all_X = np.vstack(all_X)
        all_Y_reg = np.vstack(all_Y_reg)
        all_Y_class = np.vstack(all_Y_class)
        
        return all_X, all_Y_reg, all_Y_class

    def split(self, train_size):
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_reg_train, y_reg_test, y_class_train, y_class_test = train_test_split(self.all_X, self.all_Y_reg, self.all_Y_class, train_size=train_size)

        return X_train, X_test, y_reg_train, y_reg_test, y_class_train, y_class_test
        
    
### parameter need to control:
### model_name, batch_size, dataset_name, percentage
parser = argparse.ArgumentParser()
parser.add_argument("--model_idx", help="0 for DropoutModelPassMessageMultitask, 1 for GATDropoutPassMessageMultitask", type=int)
parser.add_argument("--batch_size", help="batch size", type=int)
parser.add_argument("--dataset_name", help="batch size", type=str)
parser.add_argument("--percentage", help="percentage of node for training", type=float)
parser.add_argument("--lr", help="learning rate", type=float, default=0.001)
args = parser.parse_args()
model_idx = args.model_idx
batch_size = args.batch_size
dataset_name = args.dataset_name
percentage = args.percentage
lr = args.lr

bridge_list, road_list, n_node, n_bridge, n_road = load_edge_list()
sample_targets = generate_sample(bridge_list, road_list, n_node, n_bridge, n_road, percentage)
print("target node list: {}".format(sample_targets))

### test on 19, 5, so dont' use these two
imageset_name = 'img' if dataset_name == 'data' else 'img_large'
train_num_sample = [100] * len(sample_targets)
### path to load training data
train_data_dir = ['./{}/data_{}_v3'.format(dataset_name, target_id) for target_id in sample_targets]


# load dataset and load into batch
train_dataset = BridgeDataset(train_num_sample, train_data_dir)
X_train, _, y_reg_train, _, _, _ = train_dataset.split(0.75)


test_targets = reserve_sample(bridge_list, road_list, n_node)
test_num_sample = [200] * len(test_targets)
### path to load training data
test_data_dir = ['./{}/data_{}_v3'.format(dataset_name, target_id) for target_id in test_targets]
test_dataset = BridgeDataset(test_num_sample, train_data_dir)
_, X_test, _, y_reg_test, _, y_class_test = test_dataset.split(0.01)

if model_idx == 11:
    print('we are here')
    from sklearn.svm import SVR
    from sklearn.multioutput import MultiOutputRegressor
    # model = SVR(kernel='rbf', C=1, epsilon=0.1)
    
    model = SVR(kernel='rbf', C=100, epsilon=0.01)
    
    wrapper = MultiOutputRegressor(model)
    wrapper.fit(X_train, y_reg_train)
    y_reg_pred = wrapper.predict(X_test)
    
    res = y_reg_pred - y_reg_test
    print(res.shape)
    all_test_err = np.mean(np.abs(res))
    print(all_test_err)
    


# f1_macro_reg, f1_micro_reg, f1_macro_cla, f1_micro_cla, mae, mse, rmse, running_time
gt_class, pred_class = [], []

for v1 in y_reg_test.reshape(-1):
    if v1 < 0.75:
        gt_class.append(0)
    else:
        gt_class.append(1)

for v1 in y_reg_pred.reshape(-1):
    if v1 < 0.75:
        pred_class.append(0)
    else:
        pred_class.append(1)

from sklearn.metrics import f1_score
# Calculate F1 score
f1 = f1_score(gt_class, pred_class, average='micro')

print("F1 Score 2 class:", f1)

gt_class, pred_class = [], []


for v1 in y_reg_test.reshape(-1):
    if v1 < 0.5:
        gt_class.append(0)
    elif v1 < 0.75:
        gt_class.append(1)
    else:
        gt_class.append(2)

for v1 in y_reg_pred.reshape(-1):
    if v1 < 0.5:
        pred_class.append(0)
    elif v1 < 0.75:
        pred_class.append(1)
    else:
        pred_class.append(2)

# Calculate F1 score
f1 = f1_score(gt_class, pred_class, average='micro')

print("F1 Score 3 class:", f1)
    
# t0 = time.time()
# train_multitask(train_dataloader, test_dataloader, percentage, model, class_weight, \
#     batch_size, num_epoch=200, model_dir=dataset_name, loss_type = loss_type, lr=lr, model_idx=model_idx)
# print('train time', time.time() - t0)