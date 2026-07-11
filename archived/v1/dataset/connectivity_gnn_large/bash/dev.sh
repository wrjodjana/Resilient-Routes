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

# python multitask_batch_only_reg_dev.py --model_idx=2 --batch_size=512 --dataset_name='data' --percentage=$percentage

# python multitask_batch_only_reg_dev.py --model_idx=3 --batch_size=512 --dataset_name='data' --percentage=$percentage

# python multitask_batch_only_reg_dev.py --model_idx=4 --batch_size=512 --dataset_name='data' --percentage=$percentage

# python multitask_batch_only_reg_dev.py --model_idx=5 --batch_size=512 --dataset_name='data' --percentage=$percentage --lr=0.01

# python multitask_batch_only_reg_dev.py --model_idx=6 --batch_size=512 --dataset_name='data' --percentage=$percentage

# python multitask_batch_only_reg_dev.py --model_idx=7 --batch_size=512 --dataset_name='data' --percentage=$percentage

python multitask_simple_regression_dev.py --model_idx=11 --batch_size=1 --dataset_name='data' --percentage=$percentage

# ################### eval ###################
# python multitask_batch_test_only_reg_dev.py --model_idx=1 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat

# python multitask_batch_test_only_reg_dev.py --model_idx=2 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat

# python multitask_batch_test_only_reg_dev.py --model_idx=3 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat

# python multitask_batch_test_only_reg_dev.py --model_idx=4 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat

# python multitask_batch_test_only_reg_dev.py --model_idx=5 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat

# python multitask_batch_test_only_reg_dev.py --model_idx=6 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat

# python multitask_batch_test_only_reg_dev.py --model_idx=7 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat

# python multitask_batch_test_only_reg_dev.py --model_idx=8 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat

# python multitask_batch_test_only_reg_dev.py --model_idx=9 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat

# python multitask_batch_test_only_reg_dev.py --model_idx=10 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat

# ################### postprocess ###################
# python criterionCorrelation_dev.py --model_idx=1 --batch_size=512 --dataset_name=$dataset_name --percentage $percentage
# python criterionCorrelation_dev.py --model_idx=2 --batch_size=512 --dataset_name=$dataset_name --percentage $percentage
# python criterionCorrelation_dev.py --model_idx=3 --batch_size=512 --dataset_name=$dataset_name --percentage $percentage
# python criterionCorrelation_dev.py --model_idx=4 --batch_size=512 --dataset_name=$dataset_name --percentage $percentage
# python criterionCorrelation_dev.py --model_idx=5 --batch_size=512 --dataset_name=$dataset_name --percentage $percentage
# python criterionCorrelation_dev.py --model_idx=6 --batch_size=512 --dataset_name=$dataset_name --percentage $percentage
# python criterionCorrelation_dev.py --model_idx=7 --batch_size=512 --dataset_name=$dataset_name --percentage $percentage
# python criterionCorrelation_dev.py --model_idx=8 --batch_size=512 --dataset_name=$dataset_name --percentage $percentage
# python criterionCorrelation_dev.py --model_idx=9 --batch_size=512 --dataset_name=$dataset_name --percentage $percentage
# python criterionCorrelation_dev.py --model_idx=10 --batch_size=512 --dataset_name=$dataset_name --percentage $percentage



# python multitask_batch_only_reg_dev.py --model_idx=6 --batch_size=64 --dataset_name='data' --percentage=$percentage
# python multitask_batch_test_only_reg_dev.py --model_idx=6 --batch_size=64 --dataset_name=$dataset_name --imageset_name=$imageset_name --percentage=$percentage --hidden_size $hidden_size --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat
# python criterionCorrelation_dev.py --model_idx=6 --batch_size=64 --dataset_name=$dataset_name --percentage $percentage


# python multitask_batch_only_reg_dev.py --model_idx=8 --batch_size=256 --dataset_name='data' --percentage=$percentage
# python multitask_batch_test_only_reg_dev.py --model_idx=8 --batch_size=64 --dataset_name=$dataset_name --imageset_name=$imageset_name --percentage=$percentage --hidden_size $hidden_size --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat
# python criterionCorrelation_dev.py --model_idx=8 --batch_size=64 --dataset_name=$dataset_name --percentage $percentage


# python multitask_batch_test_only_reg_dev.py --model_idx=1 --batch_size=512 --dataset_name=$dataset_name --imageset_name=$imageset_name \
#     --percentage=$percentage --train_sample_size $train_sample_size --total_sample_size $total_sample_size --n_feat $n_feat