"""
===================================================================
Title:          detectron2_annotate_data.py
Description:    Merge output files to a single CSV file per video
Author:         Fabian Kahl
===================================================================
"""

import numpy as np
import os
from pathlib import Path
import pandas as pd
import cv2
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-video', '--video_filepath', type=str, help='video filepath')
parser.add_argument('-npy', '--npy_dirpath', type=str, help='npy dirpath')
parser.add_argument('-time', '--duration_file', type=str, help='dirpath of duration measurement data')
parser.add_argument('-out', '--csv_out', type=str, help='path for csv output file')
args = parser.parse_args()

video_filepath = args.video_filepath
npy_dirpath = args.npy_dirpath
duration_file = args.duration_file
csv_out = args.csv_out

# Source keypoint names:
# https://github.com/facebookresearch/detectron2/blob/ebb9f8c9166765c508f8ac53d9ed2004739b28d1/detectron2/data/datasets/builtin_meta.py#L144-L167

joint_names = ["nose",
    "left_eye", "right_eye",
    "left_ear", "right_ear",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle"]

duration = float(open(duration_file, 'r').read())

pathlist = Path(npy_dirpath).rglob('*.npy')
j = 0
for path in pathlist:
    j+=1
df = pd.DataFrame()
for k in range(1, j+1):
    path = npy_dirpath+'/frame_'+str(k)+'.npy'
    try:
        npy_file = np.load(path, allow_pickle=True).tolist()[0]
        df_frame = pd.DataFrame(npy_file, columns=['X', 'Y', 'Z'], index=joint_names)
    except:
        df_frame = pd.DataFrame(index=range(17), columns=['X', 'Y', 'Z'])
    # Stack rows on cols --> one row with "col_row"
    df_frame_stacked = df_frame.stack().to_frame()
    df_frame_stacked.set_index(df_frame_stacked.index.map(''.join), inplace=True)
    df_frame_stacked = df_frame_stacked.transpose()
    
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