from random import sample
from dgl import batch
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

import dgl
from dgl.data import DGLDataset
import dgl.function as fn
from dgl.nn.pytorch import GATConv

import os
import numpy as np
import pickle
import time
from math import ceil
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score

from utils_v2_dev import *
from modelzoo_rev import *

import argparse

# dgl.seed(234)
# np.random.seed(234)
torch.manual_seed(234) #234 523 42
torch.set_printoptions(linewidth=400, precision=3)
np.set_printoptions(linewidth=400, precision=3)

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
# print("using device: {}".format(device))

def collate(samples):
    n = len(samples)
    reg_list = [samples[i].ndata['label'] for i in range(n)]
    cla_list = [samples[i].ndata['class'] for i in range(n)]
    batched_graph = dgl.batch(samples)
    return batched_graph, torch.vstack((*reg_list,)), torch.vstack((*cla_list,))

class BridgeDataset(DGLDataset):
    def __init__(self, start_id, end_id, data_dir):
        self.start_id = start_id
        self.end_id = end_id
        self.data_dir = os.path.join("connectivity_gnn_small", "data", data_dir) 
        if type(start_id) == list:
            super(BridgeDataset, self).__init__(name='bridge', hash_key={start_id[0], self.data_dir})
        else:
            super(BridgeDataset, self).__init__(name='bridge', hash_key={start_id, self.data_dir})

    def process(self):
        self.graphs = []
        start_id_list = self.start_id if type(self.start_id) == list else [self.start_id]
        end_id_list = self.end_id if type(self.end_id) == list else [self.end_id]
        data_dir_list = self.data_dir if type(self.start_id) == list else [self.data_dir]
        
        
        # print('loading {}'.format(dir))
        with open(self.data_dir+'/graph_info.pickle', 'rb') as handle:
            graph_info = pickle.load(handle)

        # Create a graph for each graph ID from the edges table.
        # First process the properties table into two dictionaries with graph IDs as keys.
        # The label and number of nodes are values.
        
        with open(self.data_dir+'/all_result_lite.pickle', 'rb') as handle:
            graph_data_all = pickle.load(handle)
        
        # load each graph
        graph_data = graph_data_all[earthquake_type]
        
        # data is directed, make it undirected
        node_1 = torch.tensor(graph_data['edge_order'][:,0].squeeze(), dtype=torch.int32)
        node_2 = torch.tensor(graph_data['edge_order'][:,1].squeeze(), dtype=torch.int32)
        edge_feat_half = torch.tensor(graph_data['edge_feat'], dtype=torch.float32)
        edge_feat = torch.cat((edge_feat_half, edge_feat_half), axis = 0)
        src = torch.cat((node_1, node_2))
        dst = torch.cat((node_2, node_1))
        
        # create undirected graph
        g = dgl.graph((src, dst), num_nodes=graph_info['n_node'])
        g.ndata['feat'] = torch.tensor(graph_data['node_feat'], dtype=torch.float32)
        g.ndata['label'] = torch.tensor(graph_data['node_res'], dtype=torch.float32)
        g.ndata['class'] = torch.tensor(graph_data['node_class'], dtype=torch.long)
        g.edata['feat'] = edge_feat

        # print(g.edges(form='uv'))

        self.graphs.append(g.to(device))

    def __getitem__(self, i):
        return self.graphs[i]

    def __len__(self):
        return len(self.graphs)

def test_multitask_record(dataset, target_node_id, model, start_id, stop_id, val_data_dir, val_img_dir, \
    class_thre, class_weight, n_class=2):
    
    # reg_loss_func = F.l1_loss if loss_type == 1 else F.mse_loss
    # cla_loss_fun = F.cross_entropy

    graph_list = [dataset[0].to(device)]
    test_idx = np.arange(stop_id-start_id)
    class_weight = torch.FloatTensor(class_weight).to(device)

    ### compute regression loss
    err_test = []

    ### compute classification loss
    confusion_matrix_reg = np.zeros((n_class, n_class))
    # confusion_matrix_cla = np.zeros((n_class, n_class))

    single_summary = []
    single_reg_result = []
    model.eval()
    ### for each target node, compute the macro/micro F1 score, L1/L2 loss on all graphs, return a matrix 200 * 5
    with torch.no_grad():
        start_time = time.time()
        g = graph_list[0]
        node_feat = g.ndata['feat']
        edge_feat = g.edata['feat']
        reg_label = g.ndata['label']
        cla_label = g.ndata['class']
        print(edge_feat.numpy().tolist())
        ### Forward
        reg_logits = model(g, node_feat, edge_feat)

        # ### Compute accuracy on training/validation/test
        # loss1 = reg_loss_func(reg_logits, reg_label)
        # loss2 = cla_loss_fun(cla_logits, cla_label.squeeze(), weight=class_weight)
        # # err_test.append((loss1+loss2).cpu().detach().numpy().item())
        # error = torch.abs(reg_logits - reg_label)
        # # print("max: {}, average: {}".format(torch.max(error), torch.mean(error)))
        
        # ### record all type of error
        # mae = F.l1_loss(reg_logits, reg_label).cpu().detach().numpy().squeeze()
        # mse = F.mse_loss(reg_logits, reg_label).cpu().detach().numpy().squeeze()
        # rmse = np.sqrt(mse)

        # ### classification based on regression result
        # class_true = cla_label.cpu().detach().numpy().squeeze()
        # class_pred_reg = reg_logits.cpu().detach().numpy().squeeze()
        # # class_pred_cla = cla_logits.cpu().detach().numpy()
        # # class_true = np.digitize(class_true, class_thre, False)
        # class_pred_reg = np.digitize(class_pred_reg, class_thre, False)
        # class_pred_cla = class_pred_cla.argmax(1)
        # for t, p in zip(class_true, class_pred_reg):
        #     confusion_matrix_reg[t, p] += 1
        # for t, p in zip(class_true, class_pred_cla):
        #     confusion_matrix_cla[t, p] += 1

        ### record the y_true and y_pred
        # f1_macro_reg = f1_score(class_true, class_pred_reg, average='macro')
        # f1_micro_reg = f1_score(class_true, class_pred_reg, average='micro')
        # f1_macro_cla = f1_score(class_true, class_pred_cla, average='macro')
        # f1_micro_cla = f1_score(class_true, class_pred_cla, average='micro')
        # running_time = time.time() - start_time
        # single_summary.append(np.array([target_node_id, graph_id, f1_macro_reg, f1_micro_reg, \
        #     mae, mse, rmse, running_time]))
        
        reg_logits_np = reg_logits.cpu().detach().numpy().reshape(-1, 1)
        print(reg_logits_np.tolist())
        reg_label_np = reg_label.cpu().detach().numpy().reshape(-1, 1)
        single_reg_result.append(np.hstack((reg_logits_np, reg_label_np)))

            #create_plot_regression(reg_logits.cpu().detach().numpy(), val_data_dir, val_img_dir, graph_id)
        # print('err_test: {:.3f}'.format(sum(err_test)/(num_sample)))
        # print("confusion_matrix_reg\n", confusion_matrix_reg)
        # print("per class accuracy from reg: ", np.diag(confusion_matrix_reg)/np.sum(confusion_matrix_reg, 1))
        # print("confusion_matrix_cla\n", confusion_matrix_cla)
        # print("per class accuracy from cla: ", np.diag(confusion_matrix_cla)/np.sum(confusion_matrix_cla, 1))
        
    return reg_logits_np.tolist()

### parameter need to control:
### model_name, batch_size, dataset_name, percentage
parser = argparse.ArgumentParser()
parser.add_argument("--model_idx", help="0, 1, 2", type=int)
parser.add_argument("--batch_size", help="batch size", type=int)
parser.add_argument("--dataset_name", help="batch size", type=str)
parser.add_argument("--imageset_name", help="imageset name", type=str)
parser.add_argument("--earthquake_type", help="major, moderate, minor", type=str)
parser.add_argument("--percentage", help="percentage of node for training", type=float)
parser.add_argument('--train_sample_size', help="sample size of each train target point", nargs='?', type=int, default=200)
parser.add_argument('--total_sample_size', help="total sample size of each target point", nargs='?', type=int, default=300)
parser.add_argument('--target_node_id', help="target node id", nargs='?', type=int, default=0)
parser.add_argument('--n_feat', help="number of feature", nargs='?', type=int, default=6)
args = parser.parse_args()
model_idx = args.model_idx
batch_size = args.batch_size
dataset_name = args.dataset_name
imageset_name = args.imageset_name
earthquake_type = args.earthquake_type
percentage = args.percentage
train_sample_size = args.train_sample_size
total_sample_size = args.total_sample_size
target_node_id = args.target_node_id
n_feat = args.n_feat

bridge_list, road_list, n_node, n_bridge, n_road = load_edge_list()
### randomly select train target node

# train_targets = generate_sample(bridge_list, road_list, n_node, n_bridge, n_road, percentage)
# print("train target list: {}".format(train_targets))
# print("total number of node: {}".format(n_node))
# ### select rest of 50% of node as test target node
# #test_targets = np.random.choice(np.delete(np.arange(n_node), train_targets), int(0.5*n_node), replace=False)
# test_targets = reserve_sample(bridge_list, road_list, n_node) #[14] #reserve_sample(bridge_list, road_list, n_node)
# print("test target list: {}".format(test_targets))
# all_targets = test_targets

class_weight = [7.0, 1.0]       # class weight for classification
class_thre = [0.75]              # threhold for difference class
reg_num = 1                     # num of regression class
cla_num = len(class_thre) + 1   # num of classification class

### load the model
if model_idx == 1:
    model = GraphSageConv(n_feat, 512, reg_num, cla_num).to(device)
if model_idx == 2:
    model = GraphSageConv_3layer(n_feat, 512, reg_num, cla_num).to(device)
if model_idx == 3:
    model = GraphSageConv_1layer(n_feat, 512, reg_num, cla_num).to(device)
if model_idx == 4:
    model = GraphSageConv(n_feat, 32, reg_num, cla_num).to(device)
if model_idx == 5:
    model = GraphSageConv(n_feat, 512, reg_num, cla_num).to(device)
if model_idx == 6:
    model = GraphSageConv_xe_only(n_feat, 512, reg_num, cla_num).to(device)
if model_idx == 7:
    model = GraphSageConv_xn_only(n_feat, 512, reg_num, cla_num).to(device)
if model_idx == 8:
    model = ModelGAT(n_feat, 512, reg_num).to(device)
if model_idx == 9:
    model = ModelGCN(n_feat, 512, reg_num).to(device)
if model_idx == 10:
    model = ModelFCNN(n_feat, 512, reg_num).to(device)
    
model_name = model.__class__.__name__
checkpoint = torch.load('./connectivity_gnn_small/saved_model_dev/{}_{}_{}_{}.pth'.format(model_idx, batch_size, dataset_name, percentage), map_location=device)
model.load_state_dict(checkpoint['model_state_dict'])

result_summary = []
reg_pred_summary = []

val_dir = 'data_{}_v2'.format(target_node_id)    # path to load different data
img_dir = 'img_reg_{}_v2'.format(target_node_id)  # path to save the prediction
start_id, stop_id = train_sample_size, total_sample_size
val_dataset = BridgeDataset(train_sample_size, total_sample_size, val_dir)

reg_logits_np = test_multitask_record(val_dataset, 0, model, start_id, stop_id, val_dir, img_dir, \
    class_thre=class_thre, class_weight=class_weight, n_class=len(class_thre)+1)


### test on each test node
# for target_node_id in test_targets:
#     if target_node_id in train_targets:
#         val_dir = './{}/data_{}_v2'.format(dataset_name, target_node_id)    # path to load different data
#         img_dir = './{}/img_reg_{}_v2'.format(imageset_name, target_node_id)  # path to save the prediction
#         start_id, stop_id = train_sample_size, total_sample_size
#         val_dataset = BridgeDataset(train_sample_size, total_sample_size, val_dir)
#     else:
#         val_dir = './{}/data_{}_v2'.format(dataset_name, target_node_id)    # path to load different data
#         img_dir = './{}/img_reg_{}_v2'.format(imageset_name, target_node_id)  # path to save the prediction
#         start_id, stop_id = 0, total_sample_size
#         val_dataset = BridgeDataset(0, total_sample_size, val_dir)

#     single_summary, single_reg_pred = test_multitask_record(val_dataset, target_node_id, model, start_id, stop_id, val_dir, img_dir, \
#         class_thre=class_thre, class_weight=class_weight, n_class=len(class_thre)+1)
    
#     result_summary.append(single_summary)
#     reg_pred_summary.append(single_reg_pred)


# result_summary = np.vstack(result_summary)
# # (model_name, batch_size, dataset_name), (percentage thre)
# np.savetxt("{}_{}_{}_{}_result.csv".format(model_idx, batch_size, \
#     dataset_name, percentage), result_summary, delimiter=',', \
#     header="target_node_id, graph_id, f1_macro_reg, f1_micro_reg, mae, mse, rmse, running_time")

# reg_pred_summary = np.vstack(reg_pred_summary)
# # (model_name, batch_size, dataset_name), (percentage thre)
# np.savetxt("reg_{}_{}_{}_{}_result.csv".format(model_idx, batch_size, \
#     dataset_name, percentage), reg_pred_summary, delimiter=',', \
#     header="prediction, ground_truth")