# ===================================================================
# Title:          movenet.sh
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
	out=./${filename_no_ending/vid/out}/
	npy="$out"npy/
	out_final=$(dirname "${filename_no_ending/vid/csv_movenet}.csv")/
	if [ ! -d "$out" ]; then
	    mkdir -p "$out"
	fi
	if [ ! -d "$out_final" ]; then
	    mkdir -p "$out_final"
	fi

 	# Capture the start and end time to calculate processing time for the demo
	start=$(date +%s.%N)
	python movenet.py --video-path $filename --out-video-root $out
	end=$(date +%s.%N)
	diff=$(echo "$end - $start" | bc)
	echo "Running time in sec: $diff"
	output_time="${filename_no_ending/vid/out}_runtime.log"
	echo "$diff" > $output_time

	# Run a second Python script that harmonizes the output to a single CSV file looking similar for all frameworks
	python movenet_annotate_data.py -npy $npy -p $filename -time $output_time -out $out_final
done
