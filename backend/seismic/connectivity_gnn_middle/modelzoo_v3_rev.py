import torch
import torch.nn as nn

import dgl.function as fn
from dgl.nn.pytorch import GATConv, GraphConv

class SAGEConvPassMessage(nn.Module):
    def __init__(self, in_feat, out_feat):
        super(SAGEConvPassMessage, self).__init__()
        # A linear submodule for projecting the input and neighbor feature to the output.
        self.linear = nn.Linear(in_feat * 2+1, out_feat)

    def forward(self, g, hn, he):
        # g.ndata['hn'], hn stores the input node features
        # g.edata['he'], he stores the input edge features
        with g.local_scope():
            g.ndata['hn'] = hn
            g.edata['he'] = he
            # update_all is a message passing API.
            # g.update_all(message_func=fn.copy_u('h', 'm'), reduce_func=fn.mean('m', 'h_N'))
            g.update_all(fn.copy_u('hn', 'm'), fn.sum('m', 'hn_aggr'))
            g.update_all(fn.copy_e('he', 'm'), fn.sum('m', 'he_aggr'))
            
            hn_aggr = g.ndata['hn_aggr']
            he_aggr = g.ndata['he_aggr']
            h_total = torch.cat([hn, hn_aggr, he_aggr], dim=1)
            return self.linear(h_total)

class SAGEConvPassMessage_xe_only(nn.Module):
    def __init__(self, in_feat, out_feat):
        super(SAGEConvPassMessage_xe_only, self).__init__()
        # A linear submodule for projecting the input and neighbor feature to the output.
        self.linear = nn.Linear(in_feat+1, out_feat)

    def forward(self, g, hn, he):
        # g.ndata['hn'], hn stores the input node features
        # g.edata['he'], he stores the input edge features
        with g.local_scope():
            g.edata['he'] = he
            # update_all is a message passing API.
            # g.update_all(message_func=fn.copy_u('h', 'm'), reduce_func=fn.mean('m', 'h_N'))
            g.update_all(fn.copy_e('he', 'm'), fn.sum('m', 'he_aggr'))
            
            he_aggr = g.ndata['he_aggr']
            h_total = torch.cat([hn, he_aggr], dim=1)
            return self.linear(h_total)

class SAGEConvPassMessage_xn_only(nn.Module):
    def __init__(self, in_feat, out_feat):
        super(SAGEConvPassMessage_xn_only, self).__init__()
        # A linear submodule for projecting the input and neighbor feature to the output.
        self.linear = nn.Linear(in_feat * 2, out_feat)

    def forward(self, g, hn, he):
        # g.ndata['hn'], hn stores the input node features
        # g.edata['he'], he stores the input edge features
        with g.local_scope():
            g.ndata['hn'] = hn
            # update_all is a message passing API.
            # g.update_all(message_func=fn.copy_u('h', 'm'), reduce_func=fn.mean('m', 'h_N'))
            g.update_all(fn.copy_u('hn', 'm'), fn.sum('m', 'hn_aggr'))
            
            hn_aggr = g.ndata['hn_aggr']
            h_total = torch.cat([hn, hn_aggr], dim=1)
            return self.linear(h_total)

class RegressionBranch(nn.Module):
    def __init__(self, in_feat, out_feat):
        super(RegressionBranch, self).__init__()
        # A linear submodule for projecting the input and neighbor feature to the output.
        self.linear1 = nn.Linear(in_feat * 2+1, in_feat)
        self.linear2 = nn.Linear(in_feat, in_feat)
        self.linear3 = nn.Linear(in_feat, out_feat)

    def forward(self, g, hn, he):
        # g.ndata['hn'], hn stores the input node features
        # g.edata['he'], he stores the input edge features
        with g.local_scope():
            g.ndata['hn'] = hn
            g.edata['he'] = he
            # update_all is a message passing API.
            # g.update_all(message_func=fn.copy_u('h', 'm'), reduce_func=fn.mean('m', 'h_N'))
            g.update_all(fn.copy_u('hn', 'm'), fn.sum('m', 'hn_aggr'))
            g.update_all(fn.copy_e('he', 'm'), fn.sum('m', 'he_aggr'))

            hn_aggr = g.ndata['hn_aggr']
            he_aggr = g.ndata['he_aggr']
            h_total = torch.cat([hn, hn_aggr, he_aggr], dim=1)

            h = self.linear1(h_total)
            h = torch.relu(h)
            h = self.linear2(h)
            h = torch.relu(h)
            h = self.linear3(h)
            return h

class RegressionBranch_xe_only(nn.Module):
    def __init__(self, in_feat, out_feat):
        super(RegressionBranch_xe_only, self).__init__()
        # A linear submodule for projecting the input and neighbor feature to the output.
        self.linear1 = nn.Linear(in_feat+1, in_feat)
        self.linear2 = nn.Linear(in_feat, in_feat)
        self.linear3 = nn.Linear(in_feat, out_feat)

    def forward(self, g, hn, he):
        # g.ndata['hn'], hn stores the input node features
        # g.edata['he'], he stores the input edge features
        with g.local_scope():
            g.edata['he'] = he
            # update_all is a message passing API.
            # g.update_all(message_func=fn.copy_u('h', 'm'), reduce_func=fn.mean('m', 'h_N'))
            g.update_all(fn.copy_e('he', 'm'), fn.sum('m', 'he_aggr'))

            he_aggr = g.ndata['he_aggr']
            h_total = torch.cat([hn, he_aggr], dim=1)

            h = self.linear1(h_total)
            h = torch.relu(h)
            h = self.linear2(h)
            h = torch.relu(h)
            h = self.linear3(h)
            return h

class RegressionBranch_xn_only(nn.Module):
    def __init__(self, in_feat, out_feat):
        super(RegressionBranch_xn_only, self).__init__()
        # A linear submodule for projecting the input and neighbor feature to the output.
        self.linear1 = nn.Linear(in_feat * 2, in_feat)
        self.linear2 = nn.Linear(in_feat, in_feat)
        self.linear3 = nn.Linear(in_feat, out_feat)

    def forward(self, g, hn, he):
        # g.ndata['hn'], hn stores the input node features
        # g.edata['he'], he stores the input edge features
        with g.local_scope():
            g.ndata['hn'] = hn
            # update_all is a message passing API.
            # g.update_all(message_func=fn.copy_u('h', 'm'), reduce_func=fn.mean('m', 'h_N'))
            g.update_all(fn.copy_u('hn', 'm'), fn.sum('m', 'hn_aggr'))

            hn_aggr = g.ndata['hn_aggr']
            h_total = torch.cat([hn, hn_aggr], dim=1)

            h = self.linear1(h_total)
            h = torch.relu(h)
            h = self.linear2(h)
            h = torch.relu(h)
            h = self.linear3(h)
            return h

class RegressionBranch_GAT(nn.Module):
    def __init__(self, in_feat, out_feat):
        super(RegressionBranch_GAT, self).__init__()
        # A linear submodule for projecting the input and neighbor feature to the output.
        self.linear1 = nn.Linear(in_feat*2+1, in_feat)
        self.linear2 = nn.Linear(in_feat, in_feat)
        self.linear3 = nn.Linear(in_feat, out_feat)

    def forward(self, g, h, he):
        # g.ndata['hn'], hn stores the input node features
        # g.edata['he'], he stores the input edge features
        with g.local_scope():
            g.ndata['hn'] = h
            g.edata['he'] = he
            # update_all is a message passing API.
            # g.update_all(message_func=fn.copy_u('h', 'm'), reduce_func=fn.mean('m', 'h_N'))
            g.update_all(fn.copy_u('hn', 'm'), fn.sum('m', 'hn_aggr'))
            g.update_all(fn.copy_e('he', 'm'), fn.sum('m', 'he_aggr'))

            hn_aggr = g.ndata['hn_aggr']
            he_aggr = g.ndata['he_aggr']
            h_total = torch.cat([h, hn_aggr, he_aggr], dim=1)
            
            h = self.linear1(h_total)
            h = torch.relu(h)
            h = self.linear2(h)
            h = torch.relu(h)
            h = self.linear3(h)
            return h

class RegressionBranch_GCN(nn.Module):
    def __init__(self, in_feat, out_feat):
        super(RegressionBranch_GCN, self).__init__()
        # A linear submodule for projecting the input and neighbor feature to the output.
        self.linear1 = nn.Linear(in_feat*2+1, in_feat)
        self.linear2 = nn.Linear(in_feat, in_feat)
        self.linear3 = nn.Linear(in_feat, out_feat)

    def forward(self, g, h, he):
        # g.ndata['hn'], hn stores the input node features
        # g.edata['he'], he stores the input edge features
        with g.local_scope():
            g.ndata['hn'] = h
            g.edata['he'] = he
            # update_all is a message passing API.
            # g.update_all(message_func=fn.copy_u('h', 'm'), reduce_func=fn.mean('m', 'h_N'))
            g.update_all(fn.copy_u('hn', 'm'), fn.sum('m', 'hn_aggr'))
            g.update_all(fn.copy_e('he', 'm'), fn.sum('m', 'he_aggr'))

            hn_aggr = g.ndata['hn_aggr']
            he_aggr = g.ndata['he_aggr']
            h_total = torch.cat([h, hn_aggr, he_aggr], dim=1)
            
            h = self.linear1(h_total)
            h = torch.relu(h)
            h = self.linear2(h)
            h = torch.relu(h)
            h = self.linear3(h)
            return h

class RegressionBranch_FCN(nn.Module):
    def __init__(self, in_feat, h_feat, out_feat):
        super(RegressionBranch_FCN, self).__init__()
        # A linear submodule for projecting the input and neighbor feature to the output.
        self.linear1 = nn.Linear(in_feat, h_feat)
        self.linear2 = nn.Linear(h_feat, h_feat)
        self.linear3 = nn.Linear(h_feat, out_feat)

    def forward(self, g, h, he):
        # g.ndata['hn'], hn stores the input node features
        # g.edata['he'], he stores the input edge features
        
        h = self.linear1(h)
        h = torch.relu(h)
        h = self.linear2(h)
        h = torch.relu(h)
        h = self.linear3(h)
        return h



class ClassificationBranch(nn.Module):
    def __init__(self, in_feat, out_feat):
        super(ClassificationBranch, self).__init__()
        # A linear submodule for projecting the input and neighbor feature to the output.
        self.linear1 = nn.Linear(in_feat * 2+1, in_feat)
        self.linear2 = nn.Linear(in_feat, in_feat)
        self.linear3 = nn.Linear(in_feat, out_feat)

    def forward(self, g, hn, he):
        # g.ndata['hn'], hn stores the input node features
        # g.edata['he'], he stores the input edge features
        with g.local_scope():
            g.ndata['hn'] = hn
            g.edata['he'] = he
            # update_all is a message passing API.
            # g.update_all(message_func=fn.copy_u('h', 'm'), reduce_func=fn.mean('m', 'h_N'))
            g.update_all(fn.copy_u('hn', 'm'), fn.sum('m', 'hn_aggr'))
            g.update_all(fn.copy_e('he', 'm'), fn.sum('m', 'he_aggr'))

            hn_aggr = g.ndata['hn_aggr']
            he_aggr = g.ndata['he_aggr']
            h_total = torch.cat([hn, hn_aggr, he_aggr], dim=1)

            h = self.linear1(h_total)
            h = torch.relu(h)
            h = self.linear2(h)
            h = torch.relu(h)
            h = self.linear3(h)
            return h

class ModelPassMessage(nn.Module):
    # original model
    def __init__(self, in_feats, h_feats, num_classes):
        super(ModelPassMessage, self).__init__()
        self.conv1 = SAGEConvPassMessage(in_feats, h_feats)
        self.convmid1 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid2 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid3 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid4 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid5 = SAGEConvPassMessage(h_feats, h_feats)
        self.conv2 = SAGEConvPassMessage(h_feats, num_classes)

    def forward(self, g, node_feat, edge_feat):
        h = self.conv1(g, node_feat, edge_feat)
        h = torch.relu(h)
        h = self.convmid1(g, h, edge_feat)
        h = torch.relu(h)
        h = self.convmid2(g, h, edge_feat)
        h = torch.relu(h)
        h = self.convmid3(g, h, edge_feat)
        h = torch.relu(h)
        h = self.convmid4(g, h, edge_feat)
        h = torch.relu(h)
        h = self.convmid5(g, h, edge_feat)
        h = torch.sigmoid(h)
        h = self.conv2(g, h, edge_feat)
        return h

class DropoutModelPassMessage(nn.Module):
    # original model with dropout
    def __init__(self, in_feats, h_feats, num_classes):
        super(DropoutModelPassMessage, self).__init__()
        self.conv1 = SAGEConvPassMessage(in_feats, h_feats)
        self.convmid1 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid2 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid3 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid4 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid5 = SAGEConvPassMessage(h_feats, h_feats)
        self.conv2 = SAGEConvPassMessage(h_feats, num_classes)
        self.drop = nn.Dropout(p=0.2)
    def forward(self, g, node_feat, edge_feat):
        h = self.conv1(g, node_feat, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid1(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid2(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid3(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid4(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid5(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.conv2(g, h, edge_feat)
        return h

class DropoutModelPassMessageLessLayer(nn.Module):
    # original model with dropout
    def __init__(self, in_feats, h_feats, num_classes):
        super(DropoutModelPassMessageLessLayer, self).__init__()
        self.conv1 = SAGEConvPassMessage(in_feats, h_feats)
        self.convmid1 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid2 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid3 = SAGEConvPassMessage(h_feats, h_feats)
        self.conv2 = SAGEConvPassMessage(h_feats, num_classes)
        self.drop = nn.Dropout(p=0.2)
    def forward(self, g, node_feat, edge_feat):
        h = self.conv1(g, node_feat, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid1(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid2(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid3(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.conv2(g, h, edge_feat)
        return h

class ResidualModelPassMessage(nn.Module):
    # add residue block
    def __init__(self, in_feats, h_feats, num_classes):
        super(ResidualModelPassMessage, self).__init__()
        self.conv1 = SAGEConvPassMessage(in_feats, h_feats)
        self.convmid1 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid2 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid3 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid4 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid5 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid6 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid7 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid8 = SAGEConvPassMessage(h_feats, h_feats)
        self.conv2 = SAGEConvPassMessage(h_feats, num_classes)
    def forward(self, g, node_feat, edge_feat):
        h = self.conv1(g, node_feat, edge_feat)
        h = torch.relu(h) + h
        h = self.convmid1(g, h, edge_feat)
        h = torch.relu(h) + h
        h = self.convmid2(g, h, edge_feat)
        h = torch.relu(h) + h
        h = self.convmid3(g, h, edge_feat)
        h = torch.relu(h) + h
        h = self.convmid4(g, h, edge_feat)
        h = torch.relu(h) + h
        h = self.convmid5(g, h, edge_feat)
        h = torch.sigmoid(h)
        h = self.convmid6(g, h, edge_feat)
        h = torch.relu(h) + h
        h = self.convmid7(g, h, edge_feat)
        h = torch.relu(h) + h
        h = self.convmid8(g, h, edge_feat)
        h = torch.sigmoid(h)
        h = self.conv2(g, h, edge_feat)
        return h

class ResidualDropoutModelPassMessage(nn.Module):
    # add residue block
    # add dropout layer
    def __init__(self, in_feats, h_feats, num_classes):
        super(ResidualDropoutModelPassMessage, self).__init__()
        self.conv1 = SAGEConvPassMessage(in_feats, h_feats)
        self.convmid1 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid2 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid3 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid4 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid5 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid6 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid7 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid8 = SAGEConvPassMessage(h_feats, h_feats)
        self.conv2 = SAGEConvPassMessage(h_feats, num_classes)
        self.drop = nn.Dropout(p=0.2)
    def forward(self, g, node_feat, edge_feat):
        h = self.conv1(g, node_feat, edge_feat)
        h = self.drop(torch.relu(h) + h)
        h = self.convmid1(g, h, edge_feat)
        h = self.drop(torch.relu(h) + h)
        h = self.convmid2(g, h, edge_feat)
        h = self.drop(torch.relu(h) + h)
        h = self.convmid3(g, h, edge_feat)
        h = self.drop(torch.relu(h) + h)
        h = self.convmid4(g, h, edge_feat)
        h = self.drop(torch.relu(h) + h)
        h = self.convmid5(g, h, edge_feat)
        h = self.drop(torch.relu(h) + h)
        h = self.convmid6(g, h, edge_feat)
        h = self.drop(torch.relu(h) + h)
        h = self.convmid7(g, h, edge_feat)
        h = self.drop(torch.relu(h) + h)
        h = self.convmid8(g, h, edge_feat)
        h = self.drop(torch.relu(h) + h)
        h = self.conv2(g, h, edge_feat)
        return h

class GATDropoutPassMessage(nn.Module):
    def __init__(self, in_feats, h_feats, num_classes, n_head = 8, feat_drop = 0.2):
        super(GATDropoutPassMessage, self).__init__()
        self.conv1 = GATConv(2*in_feats+1, h_feats, num_heads=n_head, feat_drop=feat_drop)
        self.convmid1 = GATConv(h_feats*n_head, h_feats, num_heads=n_head, feat_drop=feat_drop)
        self.convmid2 = GATConv(h_feats*n_head, h_feats, num_heads=num_classes, feat_drop=feat_drop)
        self.convmid3 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid4 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid5 = SAGEConvPassMessage(h_feats, h_feats)
        self.conv2 = SAGEConvPassMessage(h_feats, num_classes)
        self.drop = nn.Dropout(p=0.2)
    def forward(self, g, hn, he):
        with g.local_scope():
            g.ndata['hn'] = hn
            g.edata['he'] = he

            g.update_all(fn.copy_u('hn', 'm'), fn.sum('m', 'hn_aggr'))
            g.update_all(fn.copy_e('he', 'm'), fn.sum('m', 'he_aggr'))

            hn_aggr = g.ndata['hn_aggr']
            he_aggr = g.ndata['he_aggr']

            h_total = torch.cat([hn, hn_aggr, he_aggr], dim=1)

            h = self.conv1(g, h_total)
            h = h.view(-1, h.size(1) * h.size(2))
            h = self.drop(torch.relu(h))

            h = self.convmid1(g, h)
            h = h.view(-1, h.size(1) * h.size(2))
            h = self.drop(torch.relu(h))

            h = self.convmid2(g, h)
            h = h.view(-1, h.size(1) * h.size(2))
            h = self.drop(torch.relu(h))
            
            h = self.convmid3(g, h, he)
            h = self.drop(torch.relu(h))
            h = self.convmid4(g, h, he)
            h = self.drop(torch.relu(h))
            h = self.convmid5(g, h, he)
            h = self.drop(torch.relu(h))
            h = self.conv2(g, h, he)

            return h

class GATDropoutPassMessageLessLayer(nn.Module):
    def __init__(self, in_feats, h_feats, num_classes, n_head = 8, feat_drop = 0.2):
        super(GATDropoutPassMessageLessLayer, self).__init__()
        self.conv1 = GATConv(2*in_feats+1, h_feats, num_heads=n_head, feat_drop=feat_drop)
        self.convmid1 = GATConv(h_feats*n_head, h_feats, num_heads=num_classes, feat_drop=feat_drop)
        self.convmid3 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid4 = SAGEConvPassMessage(h_feats, h_feats)
        self.conv2 = SAGEConvPassMessage(h_feats, num_classes)
        self.drop = nn.Dropout(p=0.2)
    def forward(self, g, hn, he):
        with g.local_scope():
            g.ndata['hn'] = hn
            g.edata['he'] = he

            g.update_all(fn.copy_u('hn', 'm'), fn.sum('m', 'hn_aggr'))
            g.update_all(fn.copy_e('he', 'm'), fn.sum('m', 'he_aggr'))

            hn_aggr = g.ndata['hn_aggr']
            he_aggr = g.ndata['he_aggr']

            h_total = torch.cat([hn, hn_aggr, he_aggr], dim=1)

            h = self.conv1(g, h_total)
            h = h.view(-1, h.size(1) * h.size(2))
            h = self.drop(torch.relu(h))

            h = self.convmid1(g, h)
            h = h.view(-1, h.size(1) * h.size(2))
            h = self.drop(torch.relu(h))
            
            h = self.convmid3(g, h, he)
            h = self.drop(torch.relu(h))
            h = self.convmid4(g, h, he)
            h = self.drop(torch.relu(h))
            h = self.conv2(g, h, he)

            return h

class DropoutModelPassMessageOneLayerRegonly(nn.Module):
    # original model with dropout
    def __init__(self, in_feats, h_feats, reg_num, cla_num):
        super(DropoutModelPassMessageOneLayerRegonly, self).__init__()
        self.conv1 = SAGEConvPassMessage(in_feats, h_feats)
        self.conv2 = RegressionBranch(h_feats, reg_num)
        self.drop = nn.Dropout(p=0.2)
    def forward(self, g, node_feat, edge_feat):
        h = self.conv1(g, node_feat, edge_feat)
        h = self.drop(torch.relu(h))
        h1 = self.conv2(g, h, edge_feat)
        return h1
    

# new model

# model 1, 4, 5
class GraphSageConv(nn.Module):
    # original model with dropout
    def __init__(self, in_feats, h_feats, reg_num, cla_num):
        super(GraphSageConv, self).__init__()
        self.conv1 = SAGEConvPassMessage(in_feats, h_feats)
        self.convmid1 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid2 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid3 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid4 = SAGEConvPassMessage(h_feats, h_feats)
        self.conv2 = RegressionBranch(h_feats, reg_num)
        self.drop = nn.Dropout(p=0.1)
    def forward(self, g, node_feat, edge_feat):
        h = self.conv1(g, node_feat, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid1(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid2(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid3(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid4(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h1 = self.conv2(g, h, edge_feat)
        return h1

# model 2
class GraphSageConv_3layer(nn.Module):
    # original model with dropout
    def __init__(self, in_feats, h_feats, reg_num, cla_num):
        super(GraphSageConv_3layer, self).__init__()
        self.conv1 = SAGEConvPassMessage(in_feats, h_feats)
        self.convmid1 = SAGEConvPassMessage(h_feats, h_feats)
        self.convmid2 = SAGEConvPassMessage(h_feats, h_feats)
        self.conv2 = RegressionBranch(h_feats, reg_num)
        self.drop = nn.Dropout(p=0.1)
    def forward(self, g, node_feat, edge_feat):
        h = self.conv1(g, node_feat, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid1(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid2(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h1 = self.conv2(g, h, edge_feat)
        return h1

# model 3
class GraphSageConv_1layer(nn.Module):
    # original model with dropout
    def __init__(self, in_feats, h_feats, reg_num, cla_num):
        super(GraphSageConv_1layer, self).__init__()
        self.conv1 = SAGEConvPassMessage(in_feats, h_feats)
        self.conv2 = RegressionBranch(h_feats, reg_num)
        self.drop = nn.Dropout(p=0.1)
    def forward(self, g, node_feat, edge_feat):
        h = self.conv1(g, node_feat, edge_feat)
        h = self.drop(torch.relu(h))
        h1 = self.conv2(g, h, edge_feat)
        return h1

# model 6
class GraphSageConv_xe_only(nn.Module):
    # original model with dropout
    def __init__(self, in_feats, h_feats, reg_num, cla_num):
        super(GraphSageConv_xe_only, self).__init__()
        self.conv1 = SAGEConvPassMessage_xe_only(in_feats, h_feats)
        self.convmid1 = SAGEConvPassMessage_xe_only(h_feats, h_feats)
        self.convmid2 = SAGEConvPassMessage_xe_only(h_feats, h_feats)
        self.convmid3 = SAGEConvPassMessage_xe_only(h_feats, h_feats)
        self.convmid4 = SAGEConvPassMessage_xe_only(h_feats, h_feats)
        self.conv2 = RegressionBranch_xe_only(h_feats, reg_num)
        self.drop = nn.Dropout(p=0.1)
    def forward(self, g, node_feat, edge_feat):
        h = self.conv1(g, node_feat, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid1(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid2(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid3(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid4(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h1 = self.conv2(g, h, edge_feat)
        return h1

# model 7
class GraphSageConv_xn_only(nn.Module):
    # original model with dropout
    def __init__(self, in_feats, h_feats, reg_num, cla_num):
        super(GraphSageConv_xn_only, self).__init__()
        self.conv1 = SAGEConvPassMessage_xn_only(in_feats, h_feats)
        self.convmid1 = SAGEConvPassMessage_xn_only(h_feats, h_feats)
        self.convmid2 = SAGEConvPassMessage_xn_only(h_feats, h_feats)
        self.convmid3 = SAGEConvPassMessage_xn_only(h_feats, h_feats)
        self.convmid4 = SAGEConvPassMessage_xn_only(h_feats, h_feats)
        self.conv2 = RegressionBranch_xn_only(h_feats, reg_num)
        self.drop = nn.Dropout(p=0.1)
    def forward(self, g, node_feat, edge_feat):
        h = self.conv1(g, node_feat, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid1(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid2(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid3(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h = self.convmid4(g, h, edge_feat)
        h = self.drop(torch.relu(h))
        h1 = self.conv2(g, h, edge_feat)
        return h1

# model 8
class ModelGAT(nn.Module):
    def __init__(self, in_feats, h_feats, reg_num, n_head = 4, feat_drop = 0.2):
        super(ModelGAT, self).__init__()
        self.conv1 = GATConv(2*in_feats+1, h_feats, num_heads=n_head, feat_drop=feat_drop)
        self.convmid1 = GATConv(h_feats*n_head, h_feats, num_heads=n_head, feat_drop=feat_drop)
        self.convmid2 = GATConv(h_feats*n_head, h_feats, num_heads=n_head, feat_drop=feat_drop)
        self.convmid3 = GATConv(h_feats*n_head, h_feats, num_heads=n_head, feat_drop=feat_drop)
        self.conv2 = GATConv(h_feats*n_head, h_feats, num_heads=1, feat_drop=feat_drop)
        self.reg = RegressionBranch_GAT(h_feats, reg_num)
        self.drop = nn.Dropout(p=0.2)
    
    def forward(self, g, hn, he):
        with g.local_scope():
            g.ndata['hn'] = hn
            g.edata['he'] = he

            g.update_all(fn.copy_u('hn', 'm'), fn.sum('m', 'hn_aggr'))
            g.update_all(fn.copy_e('he', 'm'), fn.sum('m', 'he_aggr'))

            hn_aggr = g.ndata['hn_aggr']
            he_aggr = g.ndata['he_aggr']

            h_total = torch.cat([hn, hn_aggr, he_aggr], dim=1)

            h = self.conv1(g, h_total)
            h = h.view(-1, h.size(1) * h.size(2))
            h = self.drop(torch.relu(h))

            h = self.convmid1(g, h)
            h = h.view(-1, h.size(1) * h.size(2))
            h = self.drop(torch.relu(h))

            h = self.convmid2(g, h)
            h = h.view(-1, h.size(1) * h.size(2))
            h = self.drop(torch.relu(h))
            
            h = self.convmid3(g, h)
            h = h.view(-1, h.size(1) * h.size(2))
            h = self.drop(torch.relu(h))

            h = self.conv2(g, h)
            h = h.view(-1, h.size(1) * h.size(2))

            h = self.reg(g, h, he)

            return h

# model 9
class ModelGCN(nn.Module):
    def __init__(self, in_feats, h_feats, reg_num):
        super(ModelGCN, self).__init__()
        self.conv1 = GraphConv(2*in_feats+1, h_feats)
        self.convmid1 = GraphConv(h_feats, h_feats)
        self.convmid2 = GraphConv(h_feats, h_feats)
        self.convmid3 = GraphConv(h_feats, h_feats)
        self.conv2 = GraphConv(h_feats, h_feats)
        self.reg = RegressionBranch_GCN(h_feats, reg_num)
        self.drop = nn.Dropout(p=0.2)
    
    def forward(self, g, hn, he):
        with g.local_scope():
            g.ndata['hn'] = hn
            g.edata['he'] = he

            g.update_all(fn.copy_u('hn', 'm'), fn.sum('m', 'hn_aggr'))
            g.update_all(fn.copy_e('he', 'm'), fn.sum('m', 'he_aggr'))

            hn_aggr = g.ndata['hn_aggr']
            he_aggr = g.ndata['he_aggr']

            h_total = torch.cat([hn, hn_aggr, he_aggr], dim=1)

            h = self.conv1(g, h_total)
            h = self.drop(torch.relu(h))

            h = self.convmid1(g, h)
            h = self.drop(torch.relu(h))

            h = self.convmid2(g, h)
            h = self.drop(torch.relu(h))
            
            h = self.convmid3(g, h)
            h = self.drop(torch.relu(h))

            h = self.conv2(g, h)
            
            h = self.reg(g, h, he)
            
            return h

# model 10
class ModelFCNN(nn.Module):
    def __init__(self, in_feats, h_feats, reg_num):
        super(ModelFCNN, self).__init__()
        self.reg = RegressionBranch_FCN(in_feats, h_feats, reg_num)
        self.drop = nn.Dropout(p=0.2)
    
    def forward(self, g, hn, he):
        
        h = self.reg(g, hn, he)
        
        return h

