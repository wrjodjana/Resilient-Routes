from dgl import batch
import torch
import torch.nn as nn
import torch.nn.functional as F
from  torch.optim.lr_scheduler import MultiStepLR
from torch.utils.data import DataLoader, dataset

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

from utils_v4_dev import load_edge_list, generate_sample, cal_label_distribution
from modelzoo_v4_rev import *

import argparse

# dgl.seed(234)
# np.random.seed(234)
torch.manual_seed(42) #234 523 42
torch.set_printoptions(linewidth=200, precision=3)
np.set_printoptions(linewidth=400, precision=3)

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print("using device: {}".format(device))

def collate(samples):
    n = len(samples)
    reg_list = [samples[i].ndata['label'] for i in range(n)]
    cla_list = [samples[i].ndata['class'] for i in range(n)]
    batched_graph = dgl.batch(samples)
    return batched_graph, torch.vstack((*reg_list,)), torch.vstack((*cla_list,))

class BridgeDataset(DGLDataset):
    def __init__(self, num_sample, data_dir):
        self.num_sample = num_sample
        self.data_dir = data_dir
        if type(num_sample) == list:
            super(BridgeDataset, self).__init__(name='bridge', hash_key={num_sample[0], data_dir[0]})
        else:
            super(BridgeDataset, self).__init__(name='bridge', hash_key={num_sample, data_dir})

    def process(self):
        self.graphs = []
        num_sample_list = self.num_sample if type(self.num_sample) == list else [self.num_sample]
        data_dir_list = self.data_dir if type(self.num_sample) == list else [self.data_dir]
        for num_sample, dir in zip(num_sample_list, data_dir_list):
            print('loading {}'.format(dir))
            with open(dir+'/graph_info.pickle', 'rb') as handle:
                graph_info = pickle.load(handle)

            # Create a graph for each graph ID from the edges table.
            # First process the properties table into two dictionaries with graph IDs as keys.
            # The label and number of nodes are values.
            graph_id_range = [i for i in range(num_sample)]
            
            with open(dir+'/all_result.pickle', 'rb') as handle:
                graph_data_all = pickle.load(handle)
                
            for graph_id in graph_id_range:
                # load each graph
                graph_data = graph_data_all[graph_id]
                
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

                self.graphs.append(g.to(device))

    def __getitem__(self, i):
        return self.graphs[i]

    def __len__(self):
        return len(self.graphs)

def train_multitask(trainloader, testloader, percentage, model, \
    class_weight, batch_size, num_epoch=200, plot_history=True, \
    save_model=True, model_dir = 'data', loss_type = 1, lr = 0.001, model_idx=0):
    
    reg_loss_func = F.l1_loss if loss_type == 1 else F.mse_loss
    cla_loss_fun = F.cross_entropy
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = MultiStepLR(optimizer, milestones=[200], gamma=0.2)

    all_train_err = []
    all_test_err = []
    class_weight = torch.FloatTensor(class_weight).to(device)

    for e in range(num_epoch):
        err_train = []
        err_test = []
        
        model.train()
        for _, (g, reg_label, cla_label) in enumerate(trainloader):
            node_feat = g.ndata['feat']
            edge_feat = g.edata['feat']

            # Forward
            reg_logits = model(g, node_feat, edge_feat)
            loss1 = reg_loss_func(reg_logits, reg_label)
            # loss2 = cla_loss_fun(cla_logits, cla_label.squeeze(), weight=class_weight)

            # Backward
            loss = loss1 #+ loss2
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            err_train.append(loss.cpu().detach().numpy().item())
        scheduler.step()
        
        model.eval()
        with torch.no_grad():
            for _, (g, reg_label, cla_label) in enumerate(testloader):
                node_feat = g.ndata['feat']
                edge_feat = g.edata['feat']
                # Forward
                reg_logits = model(g, node_feat, edge_feat)
                loss1 = reg_loss_func(reg_logits, reg_label)
                # loss2 = cla_loss_fun(cla_logits, cla_label.squeeze(), weight=class_weight)
                err_test.append((loss1).cpu().detach().numpy().item())
        all_test_err.append(sum(err_test)/len(err_test))
        all_train_err.append(sum(err_train)/len(err_train))
        if e % 5 == 0:
            print('In epoch {}, err_train: {:.3f}, err_test: {:.3f}'.format(e, \
                sum(err_train)/len(err_train), sum(err_test)/len(err_test)))
    if plot_history:
        plt.figure()
        plt.plot(all_train_err, 'b', label='train error')
        plt.plot(all_test_err, 'r', label='test error')
        plt.legend()
        plt.ylim([0.0, 0.5])
        plt.xlabel('number of epoch')
        plt.ylabel('L1 error')
        plt.savefig('./img/img_meeting_v4/loss_2.jpg')
        plt.close('all')
    if save_model:
        # save model: (model_name, batch_size, dataset_name, percentage)
        model_name = model.__class__.__name__
        torch.save({
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict()
        }, './saved_model_dev/{}_{}_{}_{}.pth'.format(model_idx, batch_size, model_dir, percentage))

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
sample_targets = generate_sample(bridge_list, road_list, n_node, \
    n_bridge, n_road, percentage)
print("target node list: {}".format(sample_targets))

### test on 19, 5, so dont' use these two
imageset_name = 'img' if dataset_name == 'data' else 'img_large'
train_num_sample = [100] * len(sample_targets)
### path to load training data
train_data_dir = ['./{}/data_{}_v4'.format(dataset_name, target_id) for target_id in sample_targets]

loss_type = 1                   # 1 for l1 loss; 2 for l2 loss
class_thre = [0.75]              # threhold for difference class
reg_num = 1                     # num of regression class
cla_num = len(class_thre) + 1   # num of classification class

val_different = True            # default is True, test on a different node
train_and_test = True          # default is True, train a model then test

if val_different:
    # test on 19, 5
    target_node_id = 19
    val_num_sample = [100]
    val_data_dir = ['./{}/data_{}_v4'.format(dataset_name, target_node_id)]    # path to load different data
    val_img_dir = ['./{}/img_reg_{}_v4'.format(imageset_name, target_node_id)]      # path to save the prediction

# load dataset and load into batch
train_dataset = BridgeDataset(train_num_sample, train_data_dir)
# class_weight = [3.0, 1.0]       # class weight for classification
class_weight = cal_label_distribution(train_dataset, cla_num) # class weight for classification
train_batch, test_batch = torch.utils.data.random_split(train_dataset, \
    [int(sum(train_num_sample)*0.75), int(sum(train_num_sample)*0.25)])
train_dataloader = DataLoader(train_batch, batch_size=batch_size, shuffle=True,
                         collate_fn=collate)
test_dataloader = DataLoader(test_batch, batch_size=batch_size, shuffle=True,
                         collate_fn=collate)

# DropoutModelPassMessageMultitask: with batch_size 4:, hidden size 32 is better

# with batch_size = 16 the acc is the best with DropoutModelPassMessage
# with batch_size = 8 the acc is the best with GATDropoutPassMessage
if model_idx == 1:
    model = GraphSageConv(train_dataset[0].ndata['feat'].shape[1], 512, reg_num, cla_num).to(device)
if model_idx == 2:
    model = GraphSageConv_3layer(train_dataset[0].ndata['feat'].shape[1], 512, reg_num, cla_num).to(device)
if model_idx == 3:
    model = GraphSageConv_1layer(train_dataset[0].ndata['feat'].shape[1], 512, reg_num, cla_num).to(device)
if model_idx == 4:
    model = GraphSageConv(train_dataset[0].ndata['feat'].shape[1], 32, reg_num, cla_num).to(device)
if model_idx == 5:
    model = GraphSageConv(train_dataset[0].ndata['feat'].shape[1], 512, reg_num, cla_num).to(device)
if model_idx == 6:
    model = GraphSageConv_xe_only(train_dataset[0].ndata['feat'].shape[1], 512, reg_num, cla_num).to(device)
if model_idx == 7:
    model = GraphSageConv_xn_only(train_dataset[0].ndata['feat'].shape[1], 512, reg_num, cla_num).to(device)
if model_idx == 8:
    model = ModelGAT(train_dataset[0].ndata['feat'].shape[1], 512, reg_num).to(device)
if model_idx == 9:
    model = ModelGCN(train_dataset[0].ndata['feat'].shape[1], 512, reg_num).to(device)
if model_idx == 10:
    model = ModelFCNN(train_dataset[0].ndata['feat'].shape[1], 512, reg_num).to(device)

t0 = time.time()
train_multitask(train_dataloader, test_dataloader, percentage, model, class_weight, \
    batch_size, num_epoch=200, model_dir=dataset_name, loss_type = loss_type, lr=lr, model_idx=model_idx)
print('train time', time.time() - t0)