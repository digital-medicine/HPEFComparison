"""
===================================================================
Title:          openpose_annotate_data.py
Description:    Merge output files to a single CSV file per video
Author:         Fabian Kahl
===================================================================
"""

import json
import pandas as pd
import cv2
import os
import argparse
from pathlib import Path

# Source:
# https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/02_output.md#body-keypoints-in-c-python
joint_names = ["Nose", "Neck", "RShoulder", "RElbow", "RWrist", "LShoulder", "LElbow", "LWrist", "MidHip", "RHip", "RKnee", "RAnkle", "LHip", "LKnee", "LAnkle", "REye", "LEye", "REar", "LEar", "LBigToe", "LSmallToe", "LHeel", "RBigToe", "RSmallToe", "RHeel"]

parser = argparse.ArgumentParser()
parser.add_argument('-video', '--video_filepath', type=str, help='video filepath')
parser.add_argument('-json', '--json_dirpath', type=str, help='json dirpath')
parser.add_argument('-time', '--duration_file', type=str, help='dirpath of duration measurement data')
parser.add_argument('-out', '--csv_out', type=str, help='directory and filename for csv output')
args = parser.parse_args()

video_filepath = args.video_filepath
json_dirpath = args.json_dirpath
duration_file = args.duration_file
csv_out = args.csv_out

duration = float(open(duration_file, 'r', encoding='utf-16').read())

pathlist = sorted(Path(json_dirpath).rglob('*.json'))

df = pd.DataFrame()

for path in pathlist:
    json_file = json.load(open(path))
    k = json_file['people'][0]['pose_keypoints_2d']
    df_frame = pd.DataFrame([k[i:i+3] for i in range(0, len(k), 3)],  columns=['X', 'Y', 'C'], index=joint_names)

    # Stack rows on cols --> one row with "col_row"
    df_frame_stacked = df_frame.stack().to_frame()
    df_frame_stacked.set_index(df_frame_stacked.index.map(''.join), inplace=True)
    df_frame_stacked = df_frame_stacked.transpose()
    
    # Append df_frame_stacked on df containing all frames
    df = pd.concat([df, df_frame_stacked])

path_split = video_filepath.rsplit('/', 1)
vid_name_in = path_split[-1]
csv_name_out = vid_name_in.replace('.avi', '.csv')

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

path, filename = csv_out.rsplit('/', 1)
path = path + '/' + filename[:2]
csv_out = path + '/' + filename
if not os.path.exists(path):
    os.makedirs(path)
df.to_csv(csv_out, index=False)