#!/bin/sh
cd ..

# # # test
python kfold_hetero_adaptive.py --map_name='Sioux' --model_idx=16 \
    --train_data_dir_list 'data_Sioux_major_00' 'data_Sioux_minor_00' 'data_Sioux_moderate_00'  \
    --test_data_dir_list 'data_Sioux_major_00' \
    --train_num_sample_list 1 1 1  --test_num_sample_list 1  --batch_size=1 \
    --gpu=-1

# python kfold_hetero_adaptive.py --map_name='Sioux' --model_idx=16 \
#     --train_data_dir_list 'data_Sioux_major_00' 'data_Sioux_minor_00' 'data_Sioux_moderate_00'  \
#     --test_data_dir_list 'data_Sioux_moderate_00' \
#     --train_num_sample_list 1 1 1  --test_num_sample_list 1 1 1  --batch_size=1 \
#     --gpu=-1

# python kfold_hetero_adaptive.py --map_name='Sioux' --model_idx=16 \
#     --train_data_dir_list 'data_Sioux_major_00' 'data_Sioux_minor_00' 'data_Sioux_moderate_00'  \
#     --test_data_dir_list 'data_Sioux_minor_00' \
#     --train_num_sample_list 1 1 1  --test_num_sample_list 1 1 1  --batch_size=1 \
#     --gpu=-1


# python kfold_hetero_adaptive.py --map_name='EMA' --model_idx=16 \
#     --train_data_dir_list 'data_EMA_minor_00' 'data_EMA_moderate_00' 'data_EMA_major_00' \
#     --test_data_dir_list 'data_EMA_minor_00' 'data_EMA_moderate_00' 'data_EMA_major_00' \
#     --train_num_sample_list 10 10 10 --test_num_sample_list 10 10 10 --batch_size=2 \
#     --epoch=50 --conservation_loss=1 --loss=1 --gpu=0

# python kfold_hetero_adaptive.py --map_name='ANAHEIM' --model_idx=16 \
#     --train_data_dir_list 'data_ANAHEIM_minor_00_cc' 'data_ANAHEIM_moderate_00_cc' 'data_ANAHEIM_major_00_cc' \
#     --test_data_dir_list 'data_ANAHEIM_minor_00_cc' 'data_ANAHEIM_moderate_00_cc' 'data_ANAHEIM_major_00_cc' \
#     --train_num_sample_list 10 10 10 --test_num_sample_list 10 10 10 --batch_size=2 \
#     --epoch=50 --conservation_loss=1 --loss=1 --gpu=0

# python kfold_hetero_od.py --map_name='Sioux' --model_idx=13 \
#     --train_data_dir_list 'data_Sioux_minor_00' 'data_Sioux_moderate_00' 'data_Sioux_major_00'  \
#     --test_data_dir_list 'data_Sioux_minor_00' 'data_Sioux_moderate_00' 'data_Sioux_major_00' \
#     --train_num_sample_list 10 10 10 --test_num_sample_list 10 10 10 --batch_size=2 \
#     --epoch=5 --conservation_loss=1 --loss=1 --gpu=0

# python kfold_hetero_od.py --map_name='ANAHEIM' --model_idx=13 \
#     --train_data_dir_list 'data_ANAHEIM_minor_00_cc' 'data_ANAHEIM_moderate_00_cc' 'data_ANAHEIM_major_00_cc' \
#     --test_data_dir_list 'data_ANAHEIM_minor_00_cc' 'data_ANAHEIM_moderate_00_cc' 'data_ANAHEIM_major_00_cc' \
#     --train_num_sample_list 500 500 500 --test_num_sample_list 500 500 500 --batch_size=128 \
#     --epoch=50 --conservation_loss=1 --loss=1 --gpu=0

######## # # train from minor to moderate train_ratio = $train_ratio
# python kfold_hetero_od.py --map_name='Sioux' --model_idx=13 \
# --train_data_dir_list 'data_Sioux_minor_00' --test_data_dir_list 'data_Sioux_moderate_00' \
# --train_num_sample_list 10000 --test_num_sample_list 10000 --batch_size=128 \
# --epoch=200 --conservation_loss=1 --loss=1 --gpu=0

# python kfold_hetero_od.py --map_name='EMA' --model_idx=13 \
# --train_data_dir_list 'data_EMA_minor_00' --test_data_dir_list 'data_EMA_moderate_00' \
# --train_num_sample_list 10000 --test_num_sample_list 10000 --batch_size=128 \
# --epoch=200 --conservation_loss=1 --loss=1 --gpu=0

# python kfold_hetero_od.py --map_name='ANAHEIM' --model_idx=13 \
# --train_data_dir_list 'data_ANAHEIM_minor_00_cc' --test_data_dir_list 'data_ANAHEIM_moderate_00_cc' \
# --train_num_sample_list 10000 --test_num_sample_list 10000 --batch_size=128 \
# --epoch=200 --conservation_loss=1 --loss=1 --gpu=0

######### # # train from moderate to major train_ratio = $train_ratio
# python kfold_hetero_od.py --map_name='Sioux' --model_idx=13 \
# --train_data_dir_list 'data_Sioux_moderate_00' --test_data_dir_list 'data_Sioux_major_00' \
# --train_num_sample_list 10000 --test_num_sample_list 10000 --batch_size=128 \
# --epoch=200 --conservation_loss=1 --loss=1 --gpu=0

# python kfold_hetero_od.py --map_name='EMA' --model_idx=13 \
# --train_data_dir_list 'data_EMA_moderate_00' --test_data_dir_list 'data_EMA_major_00' \
# --train_num_sample_list 10000 --test_num_sample_list 10000 --batch_size=128 \
# --epoch=200 --conservation_loss=1 --loss=1 --gpu=0

# python kfold_hetero_od.py --map_name='ANAHEIM' --model_idx=13 \
# --train_data_dir_list 'data_ANAHEIM_moderate_00_cc' --test_data_dir_list 'data_ANAHEIM_major_00_cc' \
# --train_num_sample_list 10000 --test_num_sample_list 10000 --batch_size=128 \
# --epoch=200 --conservation_loss=1 --loss=1 --gpu=0


######### # # train from all to all train_ratio = $train_ratio
# python kfold_hetero_od.py --map_name='Sioux' --model_idx=13 \
#     --train_data_dir_list 'data_Sioux_minor_00' 'data_Sioux_moderate_00' 'data_Sioux_major_00'  \
#     --test_data_dir_list 'data_Sioux_minor_00' 'data_Sioux_moderate_00' 'data_Sioux_major_00' \
#     --train_num_sample_list 10000 --test_num_sample_list 10000 --batch_size=128 \
#     --epoch=200 --conservation_loss=1 --loss=1 --gpu=0

# python kfold_hetero_od.py --map_name='EMA' --model_idx=13 \
#     --train_data_dir_list 'data_EMA_minor_00' 'data_EMA_moderate_00' 'data_EMA_major_00' \
#     --test_data_dir_list 'data_EMA_minor_00' 'data_EMA_moderate_00' 'data_EMA_major_00' \
#     --train_num_sample_list 10000 --test_num_sample_list 10000 --batch_size=128 \
#     --epoch=200 --conservation_loss=1 --loss=1 --gpu=0

# python kfold_hetero_od.py --map_name='ANAHEIM' --model_idx=13 \
#     --train_data_dir_list 'data_ANAHEIM_minor_00_cc' 'data_ANAHEIM_moderate_00_cc' 'data_ANAHEIM_major_00_cc' \
#     --test_data_dir_list 'data_ANAHEIM_minor_00_cc' 'data_ANAHEIM_moderate_00_cc' 'data_ANAHEIM_major_00_cc' \
#     --train_num_sample_list 10000 --test_num_sample_list 10000 --batch_size=128 \
#     --epoch=200 --conservation_loss=1 --loss=1 --gpu=0



