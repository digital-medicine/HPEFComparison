"""
===================================================================
Title:          ultralytics_annotate_data.py
Description:    Merge output files to a single CSV file per video
Author:         Fabian Kahl
===================================================================
"""

import numpy as np
import argparse
import pandas as pd
import cv2
import os
from pathlib import Path
import re

parser = argparse.ArgumentParser()
parser.add_argument('-txt', '--txt_location', type=str, help='keypoint data .txt dir path')
parser.add_argument('-v', '--video', type=str, help='filepath of video')
parser.add_argument('-time', '--duration_location', type=str, help='filepath of duration measurement data')
parser.add_argument('-out', '--csv_out', type=str, help='output directory and name path for csv output')
args = parser.parse_args()

txt_dirpath= args.txt_location
duration_file = args.duration_location
video_filepath = args.video
csv_out = args.csv_out

# Source:
# https://docs.ultralytics.com/datasets/pose/coco/

joint_names = ["nose",
    "left_eye", "right_eye",
    "left_ear", "right_ear",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle"]


def extract_number(filename):
    match = re.search(r'(\d+)\.txt$', str(filename))
    return int(match.group(1)) if match else float('inf')

duration = float(open(duration_file, 'r').read())

path_split = video_filepath.rsplit('/', 1)
vid_name_in = path_split[-1]
csv_name_out = vid_name_in.replace('.mp4', '.csv')

pathlist = sorted(list(Path(txt_dirpath).glob(vid_name_in.split('.')[0]+'_*'+'.txt')), key=extract_number)
df = pd.DataFrame()
frame = []
for path in pathlist:
    try:
        # One person
        txt_frame = np.array(open(path).read().split(' ')[5:]).reshape(17, 3)
    except:
        # Two people
        txt_frame = np.array(open(path).read().split(' ')[60:]).reshape(17, 3)
    df_frame = pd.DataFrame(txt_frame, columns=['X', 'Y', 'Visibility'], index=joint_names)
    # Stack rows on cols --> one row with "col_row"
    df_frame_stacked = df_frame.stack().to_frame()
    df_frame_stacked.set_index(df_frame_stacked.index.map(''.join), inplace=True)
    df_frame_stacked = df_frame_stacked.transpose()
    frame.append(extract_number(path))
    
    # Append df_frame_stacked on df containing all frames
    df = pd.concat([df, df_frame_stacked])

path_split = video_filepath.rsplit('/', 1)
vid_name_in = path_split[-1]
csv_name_out = vid_name_in.replace('.mp4', '.csv')

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
    if not success:
        print("Ignoring empty video frame.")
        break
    timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
    timestamps.append(timestamp_ms)
cap.release()

df['Timestamp'] = timestamps[:len(df)]
df['Frame'] = frame
df['right_ankleVisibility'] = df['right_ankleVisibility'].str.replace('\n', '')

# Rearrange the cols to have the meta data in front
cols = df.columns.to_list()
df = df[cols[-6:] + cols[:-6]] # Move last 6 cols to the front

df.to_csv(csv_out, index=False)