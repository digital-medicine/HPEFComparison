"""
===================================================================
Title:          O_openpifpif-vita_annotate_data.py
Description:    Merge output files to a single CSV file per video
Author:         Fabian Kahl
===================================================================
"""

# openpifpaf_annotate_data.py not working, somehow openpifpaf.video is trying to open it

import json
import pandas as pd
import cv2
import os
import argparse
from pathlib import Path

# Source:
# https://openpifpaf.github.io/datasets.html#coco-person-keypoints
joint_names = ['nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear', 'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_knee', 'right_knee', 'left_ankle', 'right_ankle']

parser = argparse.ArgumentParser()
parser.add_argument('-video', '--video_filepath', type=str, help='video filepath')
parser.add_argument('-json', '--json_filepath', type=str, help='json filepath')
parser.add_argument('-time', '--duration_file', type=str, help='dirpath of duration measurement data')
parser.add_argument('-out', '--csv_out', type=str, help='directory for csv output')
args = parser.parse_args()

video_filepath = args.video_filepath
json_filepath = args.json_filepath
duration_file = args.duration_file
csv_out = args.csv_out

duration = float(open(duration_file, 'r').read())

df = pd.DataFrame()

j = 0
with open(json_filepath, 'r') as file:
    for line in file:
        frame = json.loads(line)
        try:
            k = frame['predictions'][0]['keypoints']
            df_frame = pd.DataFrame([k[i:i+3] for i in range(0, len(k), 3)],  columns=['X', 'Y', 'C'], index=joint_names)
        
        except:
            df_frame = pd.DataFrame(index=range(17), columns=['X', 'Y', 'C'])
        
        # Stack rows on cols --> one row with "col_row"
        df_frame_stacked = df_frame.stack().to_frame()
        df_frame_stacked.set_index(df_frame_stacked.index.map(''.join), inplace=True)
        df_frame_stacked = df_frame_stacked.transpose()
        
        # Append df_frame_stacked on df containing all frames
        df = pd.concat([df, df_frame_stacked])

path_split = video_filepath.rsplit('/', 1)
vid_name_in = path_split[-1]

# Fill some meta data
vid_in_split = vid_name_in.split('_')
df['Subject'] = 'Sub'+str(int(vid_in_split[0]))
df['exerciseName'] = vid_in_split[2]
df['ipad_view'] = vid_in_split[3].split('.')[0]
df['duration'] = duration

# To get timestamps
cap = cv2.VideoCapture(video_filepath)
timestamps = []
while cap.isOpened():
    success, image = cap.read()
    timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
    if not success:
        print("Ignoring empty video frame.")
        break
    timestamps.append(timestamp_ms)
cap.release()

df['Timestamp'] = timestamps
df['Frame'] = list(range(1, len(df)+1))

# Rearrange the cols to have the meta data in front
cols = df.columns.to_list()
df = df[cols[-6:] + cols[:-6]] # Move last 6 cols to the front

df.to_csv(csv_out, index=False)