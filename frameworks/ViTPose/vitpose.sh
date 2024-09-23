# ===================================================================
# Title:          vitpose.sh
# Description:    Run framework demo & merge output for every video
# Author:         Fabian Kahl
# ===================================================================

filenames=$@*/*
num_files=$(ls $filenames | wc -l)
eval "$(conda shell.bash hook)"
conda activate openmmlab
i=0
for filename in $filenames; do
	let i=i+1
	echo '##################################################'
	echo '##################################################'
	echo '##################################################'
	echo "Computing video $i out of $num_files: $filename"
	echo '##################################################'
	echo '##################################################'
	echo '##################################################'

    # Prepare the output directories
	filename_no_ending=${filename%.*}
	out=./${filename_no_ending/vid/out}/
	npy="$out"npy/
	if [ ! -d "$out" ]; then
	    mkdir -p "$out"
	fi
	out_final=$(dirname "${filename_no_ending/vid/csv_vitpose}.csv")/
	if [ ! -d "$out_final" ]; then
	    mkdir -p "$out_final"
	fi

 	# Capture the start and end time to calculate processing time for the demo
	start=$(date +%s.%N)
	python demo/body3d_two_stage_video_demo.py \
    demo/mmdetection_cfg/faster_rcnn_r50_fpn_coco.py \
    https://download.openmmlab.com/mmdetection/v2.0/faster_rcnn/faster_rcnn_r50_fpn_1x_coco/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth \
    configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/ViTPose_huge_coco_256x192.py \
    vitpose-h.pth \
    configs/body/3d_kpt_sview_rgb_vid/video_pose_lift/h36m/videopose3d_h36m_243frames_fullconv_supervised_cpn_ft.py \
    https://download.openmmlab.com/mmpose/body3d/videopose/videopose_h36m_243frames_fullconv_supervised_cpn_ft-88f5abbb_20210527.pth \
    --video-path $filename \
    --out-video-root $out \
    --rebase-keypoint-height
	end=$(date +%s.%N)
	diff=$(echo "$end - $start" | bc)
	echo "Running time in sec: $diff"
	output_time="${filename_no_ending/vid/out}_runtime.log"
	echo "$diff" > $output_time

	# Run a second Python script that harmonizes the output to a single CSV file looking similar for all frameworks
	python vitpose_annotate_data.py -npy $npy -p $filename -time $output_time -out $out_final
done
