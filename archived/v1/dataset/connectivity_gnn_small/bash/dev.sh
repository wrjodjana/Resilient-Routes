#!/bin/sh
cd ..

train_sample_size=100
total_sample_size=200
hidden_size=64
dataset_name='data'
imageset_name='img'
n_feat=4
percentage=0.8



################### train ###################
# python multitask_batch_only_reg_dev.py --model_idx=1 --batch_size=512 --dataset_name='data' --percentage=$percentage

# python multitask_batch_only_reg_dev.py --model_idx=7 --batch_size=512 --dataset_name='data' --percentage=$percentage

# # ################### eval ###################
# python multitask_batch_test_only_reg_dev.py --model_idx=1 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat

python multitask_batch_test_only_reg_dev.py --model_idx=7 --batch_size=512 --dataset_name=data --imageset_name=img \
    --percentage=0.8 --batch_size=512 --earthquake_type=major --target_node_id=18 --n_feat=4

