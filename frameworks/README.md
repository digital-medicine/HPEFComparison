For every framework, one subfolder exists with its name.

Within every subfolder, `<name of framework>.sh` was run for every framework.
This bash script ran over all video files and used either a (modified) Python script based on the demo provided by the framework or a command provided by the framework.

The bash scripts used demo Python scripts or commands to run the framework (whatever the framework provided).
The used (modified) Python scripts and their source location are part of the subfolders.

All bash scripts except `alphapose.sh` and `openpifpaf.sh` also used `<name of framework>_annotate_data.py` to merge output files to a single CSV file per video.
For `alphapose.sh` and `openpifpaf.sh` the `<name of framework>_annotate_data.ipynb` was run manually after the bash script.
All used Python scripts and their source are located in the subfolders.
