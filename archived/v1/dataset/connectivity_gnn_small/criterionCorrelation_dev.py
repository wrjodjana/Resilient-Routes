import sys
sys.path.append("..")

import argparse
import contextlib
import pickle
import random
from itertools import chain
import matplotlib
import matplotlib.pyplot as plt

import networkx as nx
import numpy as np
import scipy.stats

import matplotlib.pylab as pylab
params = {"text.usetex": False,
         'font.size': 24,
         'figure.figsize': [7.5, 10/4*3]}
pylab.rcParams.update(params)
plt.rcParams['figure.dpi'] = 200

from modelzoo_rev import *
from post_utils_dev import *

np.set_printoptions(linewidth=400, precision=3)

### parameter need to control:
### model_name, batch_size, dataset_name, percentage
parser = argparse.ArgumentParser()
parser.add_argument("--model_idx", help="0 for DropoutModelPassMessageMultitask, 1 for GATDropoutPassMessageMultitask", type=int)
parser.add_argument("--batch_size", help="batch size", type=int)
parser.add_argument("--dataset_name", help="batch size", type=str)
parser.add_argument("--percentage_list", help="percentage of node for training", nargs='+', type=float)
args = parser.parse_args()
model_idx = args.model_idx
batch_size = args.batch_size
dataset_name = args.dataset_name
percentage_list = args.percentage_list

    
for percentage in percentage_list:
    # f1_macro_reg, f1_micro_reg, f1_macro_cla, f1_micro_cla, mae, mse, rmse, running_time
    pred, gt, corr_coeff = cal_correlation(batch_size, dataset_name, model_idx, percentage)
    print("MAE: {}".format(np.mean(np.abs(pred-gt))))
    res = np.zeros((2,2))
    for p, g in zip(pred, gt):
        if g >= 0.75 and p >= 0.75:
            res[1,1] += 1
        if g >= 0.75 and p < 0.75:
            res[1,0] += 1
        if g < 0.75 and p < 0.75:
            res[0,0] += 1
        if g < 0.75 and p >= 0.75:
            res[0,1] += 1
    # print(res)
    # Calculate precision and recall
    precision = res[0,0] / (res[0,0] + res[1,0])
    recall = res[0,0] / (res[0,0] + res[0,1])

    # Calculate F1 score
    f1 = 2 * (precision * recall) / (precision + recall)
    print("MAE: {}, MSE: {}, F1: {}".format(np.mean(np.abs(pred-gt)), np.mean(np.square(pred-gt)), f1))
    
    total_num = np.sum(res)
    left_top = res[0,1] / total_num
    right_bottom = res[1,0] / total_num
    anchor1 = (0.75/2, 0.75+0.25/2)
    anchor2 = (0.75+0.25/2, 0.75/2)
    anchor3 = (0.67, 0.45)
    
    

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax1.scatter(gt, pred, s=10, zorder=10, facecolors='none', edgecolors='k', alpha=0.002)
    ax1.plot([0,1], [0,1], 'r-', alpha=0.75, zorder=20, linewidth=3)
    ax1.set_aspect('equal')
    ax1.set_xlim((0., 1))
    ax1.set_ylim((0., 1))
    ax1.set_xlabel("Ground Truth")
    ax1.set_ylabel("Prediction")
    ax1.set_title("Pearsons correlation: {}".format(round(corr_coeff, 3)))
    ax1.text(anchor3[0], anchor3[1], "$R^2=${}".format(round(corr_coeff, 2)), ha="center", va="center", zorder=10)

    # ax1.plot([0,1], [0.75,0.75], 'r-', alpha=0.75, zorder=20, linewidth=3)
    # ax1.plot([0.75,0.75], [0,1], 'r-', alpha=0.75, zorder=20, linewidth=3)
    # ax1.text(anchor1[0], anchor1[1], "{}%".format((left_top*100).round(2)), ha="center", va="center", zorder=10)
    # ax1.text(anchor2[0], anchor2[1], "{}%".format((right_bottom*100).round(2)), ha="center", va="center", zorder=10)

    plt.tight_layout()
    plt.subplots_adjust(top=0.94, bottom=0.11, right=1.0, left=0.1, hspace=0, wspace=0)
    plt.margins(0, 0)
    fig1.savefig("postprocess_dev/corr_{}_{}_{}_{}.jpg".format(model_idx, batch_size, dataset_name, percentage))

    plt.close('all')


# for percentage in percentage_list:
#     # f1_macro_reg, f1_micro_reg, f1_macro_cla, f1_micro_cla, mae, mse, rmse, running_time
#     pred, gt, corr_coeff = cal_correlation(batch_size, dataset_name, model_idx, percentage)
#     gt_class, pred_class = [], []

#     for v1 in gt:
#         if v1 < 0.75:
#             gt_class.append(0)
#         else:
#             gt_class.append(1)
    
#     for v1 in pred:
#         if v1 < 0.75:
#             pred_class.append(0)
#         else:
#             pred_class.append(1)
    
#     from sklearn.metrics import f1_score
#     # Calculate F1 score
#     f1 = f1_score(gt_class, pred_class, average='micro')

#     print("F1 Score 2 class:", f1)

# for percentage in percentage_list:
#     # f1_macro_reg, f1_micro_reg, f1_macro_cla, f1_micro_cla, mae, mse, rmse, running_time
#     pred, gt, corr_coeff = cal_correlation(batch_size, dataset_name, model_idx, percentage)
#     gt_class, pred_class = [], []

#     for v1 in gt:
#         if v1 < 0.5:
#             gt_class.append(0)
#         elif v1 < 0.75:
#             gt_class.append(1)
#         else:
#             gt_class.append(2)
    
#     for v1 in pred:
#         if v1 < 0.5:
#             pred_class.append(0)
#         elif v1 < 0.75:
#             pred_class.append(1)
#         else:
#             pred_class.append(2)
    
#     from sklearn.metrics import f1_score
#     # Calculate F1 score
#     f1 = f1_score(gt_class, pred_class, average='micro')

#     print("F1 Score 3 class:", f1)


