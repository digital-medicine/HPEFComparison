# ===================================================================
# Title:          alphapose.sh
# Description:    Run framework demo for every video
# Author:         Philipp Wegner
# ===================================================================

#!/bin/bash

INPUT_DIR=""
ALPHA_POSE_DIR=""
OUTPUT_DIR=""



for dir in $INPUT_DIR/*;
do 
        video_ID=${dir##/*}      
        mkdir -p OUTPUT_DIR/$video_ID  
        echo Processing $video_ID ...
        $ALPHA_POSE_DIR/AlphaPose/scripts/inference.sh $ALPHA_POSE_DIR/AlphaPose/configs/halpe_coco_wholebody_136/resnet/256x192_res50_lr1e-3_2x-regression.yaml $ALPHA_POSE_DIR/AlphaPose/pretrained_models/multi_domain_fast50_regression_256x192.pth $dir $OUTPUT_DIR/$video_ID
done