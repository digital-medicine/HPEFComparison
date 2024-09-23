# ===================================================================
# Title:          detectron2.sh
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
	output=${filename/vid/out}
	output_sub=$(dirname "$output")
	csv_out_dir=${output/out/csv_detectron2}
	csv_output_sub=$(dirname "$csv_out_dir")
 	csv_out=${csv_out_dir%.*}.csv
	npy=${output%.*}
	if [ ! -d "$output_sub" ]; then
	    mkdir "$output_sub"
	fi
	if [ ! -d "$csv_output_sub" ]; then
	    mkdir "$csv_output_sub"
	fi
 
 	# Capture the start and end time to calculate processing time for the demo
	start=$(date +%s.%N)
	python demo/demo.py --video-input $filename --output $output
	end=$(date +%s.%N)
	diff=$(echo "$end - $start" | bc)
	echo "Running time in sec: $diff"
	output_time="${output%.*}_runtime.log"
	echo "$diff" > $output_time
 
	# Run a second Python script that harmonizes the output to a single CSV file looking similar for all frameworks
	python detectron2_annotate_data.py -video $filename -npy $npy -time $output_time -out $csv_out
done