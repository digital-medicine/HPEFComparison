# ===================================================================
# Title:          openpifpaf.sh
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
        python -m openpifpaf.video --source $sub_dir --video-output $OUTPUT_DIR/$video/openpifpaf_tagged.mp4 --json-output $OUTPUT_DIR/$video/markers.json --checkpoint shufflenetv2k30

done