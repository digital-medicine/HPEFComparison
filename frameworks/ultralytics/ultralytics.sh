# ===================================================================
# Title:          ultralytics.sh
# Description:    Run framework demo & merge output for every video
# Author:         Fabian Kahl
# ===================================================================

filenames=$@*/*
num_files=$(ls $filenames | wc -l)
eval "$(conda shell.bash hook)"
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
	filename_blank=${filename_no_ending##*/}
	output_time=${filename_no_ending/vid/out}_runtime.log
	predict_out=runs/pose/predict/
	out=${filename_no_ending/vid/csv_ultralytics}.csv
	out_dir=$(dirname "$out")
	predict_new=$(dirname "$output_time")
	txt_new=$predict_new/$filename_blank/labels/
	if [ ! -d "$out_dir" ]; then
	    mkdir -p "$out_dir"
	fi
	if [ ! -d "$predict_new" ]; then
	    mkdir -p "$predict_new"
	fi

 	# Capture the start and end time to calculate processing time for the demo
	start=$(date +%s.%N)
	yolo pose predict model='model/yolov8x-pose-p6.pt' source=$filename conf=0.5 save_txt=True
	end=$(date +%s.%N)
	diff=$(echo "$end - $start" | bc)
	echo "Running time in sec: $diff"
	echo "$diff" > $output_time

    # Move results to correct folder
	mv $predict_out $predict_new/$filename_blank
	# Because mv sometimes is not fast enough
	sleep 10
 
 	# Run a second Python script that harmonizes the output to a single CSV file looking similar for all frameworks
	python ultralytics_annotate_data.py -txt $txt_new -v $filename -time $output_time -out $out
done
