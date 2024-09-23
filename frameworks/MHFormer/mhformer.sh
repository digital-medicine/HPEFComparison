# ===================================================================
# Title:          mhformer.sh
# Description:    Run framework demo & merge output for every video
# Author:         Fabian Kahl
# ===================================================================

filenames=$@*/*
num_files=$(ls $filenames | wc -l)
eval "$(conda shell.bash hook)"
conda activate mhformer
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
	csv_out=${filename_no_ending/video/csv_mhformer}.csv
	csv_out_dir=$(dirname "$csv_out")
	npz=${filename_no_ending/video/output}/output_3D/output_keypoints_3d.npz
	out_dir=${csv_out_dir/csv_mhformer/output}
	if [ ! -d "$csv_out_dir" ]; then
	    mkdir "$csv_out_dir"
	fi
	if [ ! -d "$out_dir" ]; then
	    mkdir "$out_dir"
	fi

 	# Capture the start and end time to calculate processing time for the demo
	start=$(date +%s.%N)
	python demo/vis.py --video $filename
	end=$(date +%s.%N)
	diff=$(echo "$end - $start" | bc)
	echo "Running time in sec: $diff"
	output_time="${filename_no_ending/video/output}_runtime.log"
	echo "$diff" > $output_time
 
	# Run a second Python script that harmonizes the output to a single CSV file looking similar for all frameworks
	python mhformer_annotate_data.py -npz $npz -v $filename -time $output_time -out $csv_out

    # Move results to HDD
	source=./demo/output/*
	destination=/mnt/disk1/out
	sudo rsync -a --remove-source-files --prune-empty-dirs $source $destination
	find $source -type d -empty -delete
done
