# ===================================================================
# Title:          mediapipe.sh
# Description:    Run framework demo & merge output for every video
# Author:         Fabian Kahl
# ===================================================================

filenames=$@*/*
num_files=$(ls $filenames | wc -l)

i=0
for filename in $filenames; do
	let i=i+1
	echo '##################################################'
	echo '##################################################'
	echo '##################################################'
	echo "Computing video $i out of $num_files $filename"
	echo '##################################################'
	echo '##################################################'
	echo '##################################################'

    # Prepare the output directories
	out=${filename/vid/out}
	out_sub=$(dirname "$out")
	out_final_h=${filename/vid/csv_mediapipe}
	out_final=${out_final_h/.mp4/.csv}
	out_final_sub=$(dirname "$out_final")
	o=${out/.mp4/.csv}
	if [ ! -d "$out_sub" ]; then
	    mkdir "$out_sub"
	fi
	if [ ! -d "$out_final_sub" ]; then
	    mkdir "$out_final_sub"
	fi

 	# Capture the start and end time to calculate processing time for the demo
	start=$(date +%s.%N)
	python MediaPipe_Pose_Landmarker.py -p $filename -o $o -oo $out
	end=$(date +%s.%N)
	diff=$(echo "$end - $start" | bc)
	echo "Running time in sec: $diff"
	output_time="${o%.*}_runtime.log"
	echo "$diff" > $output_time
 
	# Run a second Python script that harmonizes the output to a single CSV file looking similar for all frameworks
	python mediapipe_annotate_data.py -csv $o -time $output_time -out $out_final
done
