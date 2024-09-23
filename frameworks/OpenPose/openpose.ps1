# ===================================================================
# Title:          openpose.ps1
# Description:    Run framework demo & merge output for every video
# Author:         Fabian Kahl
# ===================================================================

$filenames = Get-ChildItem $args[0]
$num_files = ($filenames).Count
$i = 0

foreach ($filename in $filenames) {
    $i++
    $filename_path = $args[0] + $filename
    Write-Host '##################################################'
    Write-Host '##################################################'
    Write-Host '##################################################'
    Write-Host "Computing video $i out of ${num_files}: $filename_path"
    Write-Host '##################################################'
    Write-Host '##################################################'
    Write-Host '##################################################'

    # Prepare the output directories
    $filename_no_ending = [System.IO.Path]::GetFileNameWithoutExtension($filename_path)
    $dir_out = 'out/' + $filename_no_ending
    $output = $filename_path -replace 'vid/', 'out/'
    $csv_out = $output -replace '.avi', '.csv'
    $csv_out = $csv_out -replace 'out/', 'csv_openpose/'

 	# Capture the start and end time to calculate processing time for the demo
    $start = Get-Date
    & bin\OpenPoseDemo.exe --video $filename_path --write_json $dir_out --write_video $output --net_resolution "1312x736" --scale_gap 0.25
    $end = Get-Date
    $diff = ($end - $start).TotalSeconds
    Write-Host "Running time in sec: $diff"

    $output_time = "$($output -replace '.avi', '')_runtime.log"
    $diff | Out-File -FilePath $output_time

	# Run a second Python script that harmonizes the output to a single CSV file looking similar for all frameworks
    python openpose_annotate_data.py -video $filename_path -json $dir_out -time $output_time -out $csv_out
}
