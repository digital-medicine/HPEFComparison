# ===================================================================
# Title:          mmpose.sh
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
	csv_out=${filename_no_ending/vid/csv_mmpose}.csv
	csv_out_dir=$(dirname "$csv_out")/
	out_dir=${csv_out_dir/csv_mmpose/out}
	output_time="${filename_no_ending/vid/out}_runtime.log"
	json=${filename_no_ending/vid/out}.json
	if [ ! -d "$csv_out_dir" ]; then
	    mkdir "$csv_out_dir"
	fi
	if [ ! -d "$out_dir" ]; then
	    mkdir "$out_dir"
	fi

 	# Capture the start and end time to calculate processing time for the demo
	start=$(date +%s.%N)
	python demo/inferencer_demo.py $filename --pose3d human3d --vis-out-dir $out_dir --pred-out-dir $out_dir
	end=$(date +%s.%N)
	diff=$(echo "$end - $start" | bc)
	echo "Running time in sec: $diff"
	echo "$diff" > $output_time

	# Run a second Python script that harmonizes the output to a single CSV file looking similar for all frameworks
	python mmpose_annotate_data.py -json $json -v $filename -time $output_time -out $csv_out_dir
done
