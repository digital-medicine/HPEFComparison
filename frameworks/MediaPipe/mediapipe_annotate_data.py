"""
===================================================================
Title:          mediapipe_annotate_data.py
Description:    Merge output files to a single CSV file per video
Author:         Fabian Kahl
===================================================================
"""

import sys
import argparse
import pandas as pd
import os

parser = argparse.ArgumentParser()
parser.add_argument('-csv', '--csv_filepath', type=str, help='csv filepath')
parser.add_argument('-time', '--duration_location', type=str, help='dirpath of duration measurement data')
parser.add_argument('-out', '--csv_out', type=str, help='output filepath for csv output')
args = parser.parse_args()

csv_filepath = args.csv_filepath
duration_file = args.duration_location
csv_out = args.csv_out

duration = float(open(duration_file, 'r').read())

df = pd.read_csv(csv_filepath)
        
path_split = csv_filepath.rsplit('/', 1)
vid_name_in = path_split[-1]

# Fill some meta data
vid_in_split = vid_name_in.split('_')
df['Subject'] = 'Sub'+str(int(vid_in_split[0]))
df['exerciseName'] = vid_in_split[2]
df['ipad_view'] = vid_in_split[3].split('.')[0]
df['duration'] = duration

# Rearrange the cols to have the meta data in front
cols = df.columns.to_list()
df = df[cols[-4:] + cols[:-4]] # Move last 4 cols to the front

df.to_csv(csv_out, index=False)
