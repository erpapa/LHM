#!/bin/bash

#启用虚拟环境
eval "$(conda shell.bash hook)"
conda activate LHM

rm nohup.out 2>/dev/null
rm nohup.log 2>/dev/null

nohup python -u ./engine/pose_estimation/video2motion.py --visualize --video_dir "./example_data/" --output_path "./train_data/motion_video/" 1>nohup.out 2>nohup.log &
