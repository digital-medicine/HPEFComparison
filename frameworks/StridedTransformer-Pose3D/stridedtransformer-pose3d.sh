# ===================================================================
# Title:          stridedtransformer-pose3d.sh
# Description:    Run framework demo & merge output for every video
# Author:         Fabian Kahl
# ===================================================================

eval "$(conda shell.bash hook)"
conda activate stp3d

filenames=$@*/*
num_files=$(find $filenames -type f | wc -l)
i=0

for filename in $filenames; do
    ((i++))
    echo "##################################################"
    echo "Computing video $i out of $num_files: $filename"
    echo "##################################################"

    # Prepare the output directories
    filename_no_ending=${filename%.*}
    csv_out=${filename_no_ending/video/csv_stp3d}.csv
    csv_out_dir=$(dirname "$csv_out")
    mkdir -p "$csv_out_dir"

    npz=${filename_no_ending/video/output}/output_3D/output_keypoints_3d.npz
    out_dir=${csv_out_dir/csv_stp3d/output}
    mkdir -p "$out_dir"

 	# Capture the start and end time to calculate processing time for the demo
    start=$(date +%s.%N)
    python demo/vis.py --video "$filename"
    end=$(date +%s.%N)
    diff=$(echo "$end - $start" | bc)
    echo "Running time in sec: $diff"
    output_time="${filename_no_ending/video/output}_runtime.log"
    echo "$diff" > $output_time

	# Run a second Python script that harmonizes the output to a single CSV file looking similar for all frameworks
    python stridedtransformer-pose3d_annotate_data.py -npz $npz -v $filename -time $output_time -out $csv_out

    # Move results to HDD
    source=./demo/output/*
    destination=/mnt/disk1/out
    sudo rsync -a --remove-source-files --prune-empty-dirs $source $destination
    find $source -type d -empty -delete
done
