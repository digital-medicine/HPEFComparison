# ===================================================================
# Title:          yolov7.sh
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
	npy_out_dir=${filename_no_ending/vid/out}/
	output_time=${filename_no_ending/vid/out}_runtime.log
	out=${filename_no_ending/vid/csv_yolov7}.csv
	out_dir=$(dirname "$out")
	if [ ! -d "$npy_out_dir" ]; then
	    mkdir -p "$npy_out_dir"
	fi

	if [ ! -d "$out_dir" ]; then
	    mkdir -p "$out_dir"
	fi

 	# Capture the start and end time to calculate processing time for the demo
	start=$(date +%s.%N)
	python pose-estimate.py --source $filename --npy_out_dir $npy_out_dir --device 0
	end=$(date +%s.%N)
	diff=$(echo "$end - $start" | bc)
	echo "Running time in sec: $diff"
	echo "$diff" > $output_time

	# Run a second Python script that harmonizes the output to a single CSV file looking similar for all frameworks
	python yolov7_annotate_data.py -npy $npy_out_dir -v $filename -time $output_time -out $out
done
