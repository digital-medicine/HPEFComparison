# ===================================================================
# Title:          openpifpaf-vita.sh
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
	json=${filename_no_ending/vid/out}_openpifpaf-vita.json
	out=${filename/vid/out}
	csv_out=${filename_no_ending/vid/csv_openpifpaf-vita}.csv
	csv_out_dir=$(dirname "$csv_out")
	out_dir=$(dirname "$out")
	if [ ! -d "$csv_out_dir" ]; then
	    mkdir "$csv_out_dir"
	fi
	if [ ! -d "$out_dir" ]; then
	    mkdir "$out_dir"
	fi

 	# Capture the start and end time to calculate processing time for the demo
	start=$(date +%s.%N)
	python3 -m openpifpaf.video --source $filename --video-output $out --json-output $json --checkpoint shufflenetv2k30
	end=$(date +%s.%N)
	diff=$(echo "$end - $start" | bc)
	echo "Running time in sec: $diff"
	echo "$diff" > $output_time

	# Run a second Python script that harmonizes the output to a single CSV file looking similar for all frameworks
	python O_openpifpaf-vita_annotate_data.py -video $filename -json $json -time $output_time -out $csv_out
done
