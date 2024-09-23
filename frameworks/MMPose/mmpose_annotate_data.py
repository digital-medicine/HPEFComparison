"""
===================================================================
Title:          mmpose_annotate_data.py
Description:    Merge output files to a single CSV file per video
Author:         Fabian Kahl
===================================================================
"""

from numpy import load
import argparse
import pandas as pd
import cv2
import os
import json

parser = argparse.ArgumentParser()
parser.add_argument('-json', '--json_location', type=str, help='filepath of .json file with the keypoint data')
parser.add_argument('-v', '--video', type=str, help='filepath of video')
parser.add_argument('-time', '--duration_location', type=str, help='filepath of duration measurement data')
parser.add_argument('-out', '--csv_dir_out', type=str, help='output directory path for csv output')
args = parser.parse_args()

json_path = args.json_location
duration_file = args.duration_location
video = args.video
csv_dir_out = args.csv_dir_out

data = json.load(open(json_path))
duration = float(open(duration_file, 'r').read())

joint_names = ['Hip', 'Right hip', 'Right knee', 'Right foot',
               'Left hip', 'Left knee', 'Left foot',
               'Spine', 'Thorax', 'Nose', 'Head',
               'Left shoulder', 'Left elbow', 'Left wrist',
               'Right shoulder', 'Right elbow', 'Right wrist']

df = pd.DataFrame()
for k in range(0, len(data)):
    df_frame = pd.DataFrame(data[k]['instances'][0]['keypoints'], columns=['X', 'Y', 'Z'], index=joint_names)
    # Stack rows on cols --> one row with "col_row"
    df_frame_stacked = df_frame.stack().to_frame()
    df_frame_stacked.set_index(df_frame_stacked.index.map(''.join), inplace=True)
    df_frame_stacked = df_frame_stacked.transpose()
    
    # Append df_frame_stacked on df containing all frames
    df = pd.concat([df, df_frame_stacked])

path_split = video.rsplit('/', 1)
vid_name_in = path_split[-1]
csv_name_out = vid_name_in.replace('.mp4', '.csv')

# Fill some meta data
vid_in_split = vid_name_in.split('_')
df['Subject'] = 'Sub'+str(int(vid_in_split[0]))
df['exerciseName'] = vid_in_split[2]
df['ipad_view'] = vid_in_split[3].split('.')[0]
df['duration'] = duration

# To get timestamps
cap = cv2.VideoCapture(video)
timestamps = []
while cap.isOpened():
    success, image = cap.read()
    timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
    if not success:
        print("Ignoring empty video frame.")
        break
    timestamps.append(timestamp_ms)
df['Timestamp'] = timestamps
cap.release()
df['Frame'] = list(range(1, len(df)+1))

# Rearrange the cols to have the meta data in front
cols = df.columns.to_list()
df = df[cols[-6:] + cols[:-6]] # Move last 6 cols to the front

if not os.path.exists(csv_dir_out):
    os.mkdir(csv_dir_out)
df.to_csv(csv_dir_out + csv_name_out, index=False)

