import argparse

import os
import pickle
from itertools import product
import time
import dgl
from dgl.data import DGLDataset
import dgl.function as fn
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Subset
from sklearn.model_selection import train_test_split, KFold
from torch.utils.data import DataLoader, dataset
from torch.utils.data import ConcatDataset
from torch.autograd.functional import jacobian
from torch.optim.lr_scheduler import MultiStepLR
import networkx as nx
from modelzoo_hetero_od import *

parser = argparse.ArgumentParser()
parser.add_argument("--map_name", help="map_name", type=str)
parser.add_argument("--gpu", help="gpu", type=int, default = -1)

parser.add_argument("--train_data_dir_list", help="train_data_dir_list", type=str, nargs="+")
parser.add_argument("--test_data_dir_list", help="test_data_dir_list", type=str, nargs="+")
parser.add_argument("--train_num_sample_list", help="train_num_sample_list", type=int, nargs="+")
parser.add_argument("--test_num_sample_list", help="test_num_sample_list", type=int, nargs="+")

parser.add_argument("--model_idx", help="model_idx", type=int)
parser.add_argument("--small_sample", help="small_sample", type=float, default = 0.0)
parser.add_argument("--batch_size", help="batch_size", type=int, default = 64)
parser.add_argument("--epoch", help="epoch", type=int, default = 200)
parser.add_argument("--lr", help="lr", type=float, default = 0.001)
parser.add_argument("--loss", help="loss function", type=int, default = 1)
parser.add_argument("--conservation_loss", help="conservation_loss", type=int)

args = parser.parse_args()
train_num_sample_list = args.train_num_sample_list
test_num_sample_list = args.test_num_sample_list
train_data_dir_list = args.train_data_dir_list
test_data_dir_list = args.test_data_dir_list
map_name = args.map_name

# dgl.seed(234)
# torch.manual_seed(234)
# np.random.seed(234)
torch.set_printoptions(linewidth=200)

if args.gpu >= 0:
    device = 'cuda:{}'.format(args.gpu) if torch.cuda.is_available() else 'cpu'
else:
    device = 'cpu'
    
def collate(samples):
    n = len(samples)
    res_ratio = [samples[i].edges['connect'].data['res_ratio'] for i in range(n)]
    res_flow = [samples[i].edges['connect'].data['res_flow'] for i in range(n)]
    batched_graph = dgl.batch(samples)
    return batched_graph, torch.vstack((*res_ratio,)), torch.vstack((*res_flow,))

class TrafficAssignmentDataset(DGLDataset):
    def __init__(self, num_sample, data_dir, n_node, map_name):
        self.num_sample = num_sample
        self.data_dir = os.path.join("sta_dataset", data_dir) 
        self.n_node = n_node
        self.map_name = map_name
        self.cap_ratio = {'Sioux':1000, 'EMA':1000, 'Anaheim':800, 'ANAHEIM':800}
        self.n_od = self.get_od_shape()
        super(TrafficAssignmentDataset, self).__init__(name='bridge', hash_key={num_sample, data_dir})
     
    def process(self):
        self.graphs = []
        
        coord_all = np.loadtxt('sta_dataset/{}/coord.csv'.format(map_name), delimiter=' ')
        coord = coord_all[:, 3:]
        
        # load each graph
        with open(self.data_dir+'/data_0.pickle', 'rb') as handle:
            graph_data = pickle.load(handle)
        # print(self.data_dir, graph_id)
        ratio, flow_list = [], []
        flow, capacity = graph_data['flow'], graph_data['capacity']
        for k1, k2 in zip(graph_data['ca_list'][:,0].squeeze(), graph_data['ca_list'][:,1].squeeze()):
            ratio.append([k1, k2, flow[(int(k1)), int(k2)]/capacity[(int(k1)), int(k2)] ])
            flow_list.append([k1, k2, flow[(int(k1)), int(k2)]])
        ratio = np.vstack(ratio)
        flow_list = np.vstack(flow_list)
        
        assert(np.array_equal(ratio[:, 0].squeeze(), graph_data['ca_list'][:, 0].squeeze()))
        assert(np.array_equal(ratio[:, 1].squeeze(), graph_data['ca_list'][:, 1].squeeze()))
        
        
        # data is directed, make it undirected
        src_ncn = torch.tensor(graph_data['ca_list'][:,0].squeeze(), dtype=torch.int32)
        dst_ncn = torch.tensor(graph_data['ca_list'][:,1].squeeze(), dtype=torch.int32)
        
        ## now nodn only connect edge that od > 0 --> considering add edge feature in the future
        src_nodn = torch.tensor(graph_data['od_list'][:,0].squeeze(), dtype=torch.int32)
        dst_nodn = torch.tensor(graph_data['od_list'][:,1].squeeze(), dtype=torch.int32)
        
        hetergraph_data = {
            ('node', 'connect', 'node'): (src_ncn, dst_ncn),
            ('node', 'od', 'node'): (src_nodn, dst_nodn)
        }
        g = dgl.heterograph(hetergraph_data)

        # considier OD as node feature
        od_node_feat = torch.tensor(graph_data['demand_matrix'], dtype=torch.float32)
        coord_feat = torch.tensor(coord, dtype=torch.float32)
        connect_edge_feat = torch.tensor(graph_data['ca_list'][:, 2:], dtype=torch.float32)
        connect_edge_res_ratio = torch.tensor(ratio[:, 2:], dtype=torch.float32)
        connect_edge_res_flow = torch.tensor(flow_list[:, 2:], dtype=torch.float32)
        
        g.nodes['node'].data['feat'] = od_node_feat / 1e3 # od vector
        g.nodes['node'].data['feat_T'] = od_node_feat.T / 1e3
        g.nodes['node'].data['coord'] = coord_feat
        g.edges['connect'].data['feat'] = connect_edge_feat # feature
        # print(torch.mean(g.edges['connect'].data['feat'], dim=0))
        if 'Sioux' in map_name:
            g.edges['connect'].data['feat'] = g.edges['connect'].data['feat'] - torch.tensor([14.6331,  2.4053])
            g.edges['connect'].data['feat'][:, 0] = g.edges['connect'].data['feat'][:, 0] / 10.0
        if 'EMA' in map_name:
            g.edges['connect'].data['feat'] = g.edges['connect'].data['feat'] - torch.tensor([2.8800, 0.1721])
            g.edges['connect'].data['feat'][:, 0] = g.edges['connect'].data['feat'][:, 0] / 5.0
        if 'ANAHEIM' in map_name:
            g.edges['connect'].data['feat'] = g.edges['connect'].data['feat'] - torch.tensor([5.0934, 0.7848])
            g.edges['connect'].data['feat'][:, 0] = g.edges['connect'].data['feat'][:, 0] / 5.0

        g.edges['connect'].data['capacity'] = connect_edge_feat[:, 0:1]*self.cap_ratio[map_name] # capacity
        g.edges['connect'].data['res_ratio'] = connect_edge_res_ratio # result_ratio
        g.edges['connect'].data['res_flow'] = connect_edge_res_flow # result_flow

        self.graphs.append(g)

    def get_od_shape(self):
        with open(self.data_dir+'/data_0.pickle', 'rb') as handle:
            graph_data = pickle.load(handle)
        od_link = graph_data['od_list']
        # od_link = torch.nonzero(torch.sum(od_feat, dim=2))
        
        return od_link.shape[0]
    
    def __getitem__(self, i):
        return self.graphs[i]

    def __len__(self):
        return len(self.graphs)

def test(test_dataloader, model, args):
    time_total = 0
    min_test_loss = 1e9
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = MultiStepLR(optimizer, milestones=[100], gamma=0.2)
    
    train_loss_list, train_residue_list, test_loss_list, test_residue_list = [], [], [], []
    t0 = time.time()
    model.train()
    train_loss, train_residue = [], []
    g, edge_ratio, edge_flow = next(iter(test_dataloader))

    g = g.to(device)
    edge_ratio = edge_ratio.to(device)
    edge_flow = edge_flow.to(device)

    node_feat = g.nodes['node'].data['feat']
    edge_feat = g.edges['connect'].data['feat']

    # ratio
    pred_ratio = model(g, node_feat, edge_feat)
    # flow
    pred_flow = pred_ratio * g.edges['connect'].data['capacity'] # print this
        
    return pred_ratio, pred_flow
    
if 'Sioux' in map_name:
    n_node = 24
    map_name = 'Sioux'
if 'EMA' in map_name:
    n_node = 74
    map_name = 'EMA'
if 'Anaheim' in map_name:
    n_node = 416
    map_name = 'Anaheim'
if 'ANAHEIM' in map_name:
    n_node = 416
    map_name = 'ANAHEIM'
    
train_data_dir_list.sort()
test_data_dir_list.sort()



all_test_batch = []
for test_num_sample, test_data_dir in zip(test_num_sample_list, test_data_dir_list):
    test_dataset = TrafficAssignmentDataset(test_num_sample, test_data_dir, n_node, map_name)
    all_test_batch.append(test_dataset)
test_batch = ConcatDataset(all_test_batch)
test_dataloader = DataLoader(test_batch, batch_size=args.batch_size, shuffle=True, collate_fn=collate)

if args.model_idx == 16: model = TransformerModel_Hetero5(in_feats=n_node, h_feats=32, num_head=4).to(device)

model_name = model.__class__.__name__
file_name = '{}_{}_0.pth'.format(args.map_name, args.model_idx)
checkpoint = torch.load(f'sta_dataset/trained_model/{file_name}', map_location=device)

# checkpoint = torch.load(PATH, weights_only=True)
model.load_state_dict(checkpoint)


a, b = test(test_dataloader, model, args) ## train --> test

print(a.detach().numpy().tolist())
print(b.detach().numpy().tolist())


# if train_data_dir_list == test_data_dir_list:
#     all_data_batch = []
#     for train_num_sample, train_data_dir in zip(train_num_sample_list, train_data_dir_list):
#         train_dataset = TrafficAssignmentDataset(train_num_sample, train_data_dir, n_node, map_name)
#         all_data_batch.append(train_dataset)

#     data_batch = ConcatDataset(all_data_batch)

#     # Check the number of samples
#     n_samples = len(data_batch)
    
#     if n_samples < 2:
#         # If there's only one sample, use it for both training and testing
#         train_index = test_index = [0]
#         fold_idx = 0
        
#         train_batch = Subset(data_batch, train_index)
#         test_batch = Subset(data_batch, test_index)
        
#         train_dataloader = DataLoader(train_batch, batch_size=args.batch_size, shuffle=True, collate_fn=collate)
#         test_dataloader = DataLoader(test_batch, batch_size=args.batch_size, shuffle=True, collate_fn=collate)
        
#         if args.model_idx == 16: model = TransformerModel_Hetero5(in_feats=n_node, h_feats=32, num_head=4).to(device)
#         if args.model_idx == 17: model = TransformerModel_Hetero5(in_feats=n_node, h_feats=32, num_head=4, n_od=train_dataset.n_od, batch_size=args.batch_size).to(device)
        
#         # def load_partial_state_dict(model, state_dict):
#         #     model_state_dict = model.state_dict()
#         #     filtered_state_dict = {k: v for k, v in state_dict.items() if k in model_state_dict and v.shape == model_state_dict[k].shape}
#         #     model_state_dict.update(filtered_state_dict)
#         #     model.load_state_dict(model_state_dict)
        
#         model_name = model.__class__.__name__
#         file_name = ' '.join(train_data_dir_list) + '_' + ' '.join(test_data_dir_list) + '_15_0.pth'
#         checkpoint = torch.load(f'./trained_model/{file_name}', map_location=device)
#         # load_partial_state_dict(model, checkpoint)
        
#         # Create the model and train
#         train(train_dataloader, test_dataloader, model, args, fold_idx)
#     else:
#         # If there are at least 2 samples, proceed with KFold
#         kf = KFold(n_splits=min(2, n_samples), shuffle=True, random_state=42)
#         for fold_idx, (train_index, test_index) in enumerate(kf.split(data_batch)):
#             train_batch = Subset(data_batch, train_index)
#             test_batch = Subset(data_batch, test_index)
            
#             train_dataloader = DataLoader(train_batch, batch_size=args.batch_size, shuffle=True, collate_fn=collate)
#             test_dataloader = DataLoader(test_batch, batch_size=args.batch_size, shuffle=True, collate_fn=collate)
            
#             if args.model_idx == 16: model = TransformerModel_Hetero5(in_feats=n_node, h_feats=32, num_head=4).to(device)
#             if args.model_idx == 17: model = TransformerModel_Hetero5(in_feats=n_node, h_feats=32, num_head=4, n_od=train_dataset.n_od, batch_size=args.batch_size).to(device)

#             # Create the model and train
#             train(train_dataloader, test_dataloader, model, args, fold_idx)
# else:
#     all_train_batch, all_test_batch = [], []
#     for train_num_sample, train_data_dir in zip(train_num_sample_list, train_data_dir_list):
#         train_dataset = TrafficAssignmentDataset(train_num_sample, train_data_dir, n_node, map_name)
#         all_train_batch.append(train_dataset)
        
#     for test_num_sample, test_data_dir in zip(test_num_sample_list, test_data_dir_list):
#         test_dataset = TrafficAssignmentDataset(test_num_sample, test_data_dir, n_node, map_name)
#         all_test_batch.append(test_dataset)

#     train_batch = ConcatDataset(all_train_batch)
#     test_batch = ConcatDataset(all_test_batch)

    
#     kf = KFold(n_splits=2, shuffle=True, random_state=42)
#     for fold_idx, (train_index, test_index) in enumerate(kf.split(train_batch)):
#         print(f"Fold {fold_idx}:")
#         print(f"  Train: index={train_index}")
#         print(f"  Test:  index={test_index}")

#         train_batch_subset = Subset(train_batch, train_index)
#         test_batch_subset = Subset(test_batch, test_index)
        
#         train_dataloader = DataLoader(train_batch_subset, batch_size=args.batch_size, shuffle=True, collate_fn=collate)
#         test_dataloader = DataLoader(test_batch_subset, batch_size=args.batch_size, shuffle=True, collate_fn=collate)
        
#         # if args.model_idx == 16: model = TransformerModel_Hetero5(in_feats=n_node, h_feats=32, num_head=4, n_od=test_dataset.n_od, batch_size=args.batch_size).to(device)
#         if args.model_idx == 16: model = TransformerModel_Hetero5(in_feats=n_node, h_feats=32, num_head=4).to(device)
#         if args.model_idx == 17: model = TransformerModel_Hetero5(in_feats=n_node, h_feats=32, num_head=4, n_od=test_dataset.n_od, batch_size=args.batch_size).to(device)
        

#         # Create the model. The output has three pred_ratio for three classes.
#         train(train_dataloader, test_dataloader, model, args, fold_idx)
