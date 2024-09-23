"""
===================================================================
Title:          mhformer_annotate_data.py
Description:    Merge output files to a single CSV file per video
Author:         Fabian Kahl
===================================================================
"""

from numpy import load
import argparse
import pandas as pd
import cv2
import os

parser = argparse.ArgumentParser()
parser.add_argument('-npz', '--npz_location', type=str, help='filepath of .npz file with the keypoint data')
parser.add_argument('-v', '--video', type=str, help='filepath of video')
parser.add_argument('-time', '--duration_location', type=str, help='filepath of duration measurement data')
parser.add_argument('-out', '--csv_out', type=str, help='output directory and name path for csv output')
args = parser.parse_args()

npz = args.npz_location
duration_file = args.duration_location
video = args.video
csv_out = args.csv_out

data = load(npz)
duration = float(open(duration_file, 'r').read())
data['reconstruction'].shape

original_shape = data['reconstruction'].shape
data2 = data['reconstruction'].reshape(original_shape[0], -1)

# Source:
# https://github.com/Vegetebird/MHFormer/issues/104

cols = ['hipX', 'hipY', 'hipZ',
        'r_hipX', 'r_hipY', 'r_hipZ',
        'r_kneeX', 'r_kneeY', 'r_kneeZ',
        'r_footX', 'r_footY', 'r_footZ',
        'l_hipX', 'l_hipY', 'l_hipZ',
        'l_kneeX', 'l_kneeY', 'l_kneeZ',
        'l_footX', 'l_footY', 'l_footZ',
        'spineX', 'spineY', 'spineZ',
        'thoraxX', 'thoraxY', 'thoraxZ',
        'neckX', 'neckY', 'neckZ',
        'headX', 'headY', 'headZ',
        'l_shoulderX', 'l_shoulderY', 'l_shoulderZ',
        'l_elbowX', 'l_elbowY', 'l_elbowZ',
        'l_wristX', 'l_wristY', 'l_wristZ',
        'r_shoulderX', 'r_shoulderY', 'r_shoulderZ',
        'r_elbowX', 'r_elbowY', 'r_elbowZ',
        'r_wristX', 'r_wristY', 'r_wristZ']
df = pd.DataFrame(data2, columns=cols)

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
cap.release()

df['Timestamp'] = timestamps
df['Frame'] = list(range(1, len(df)+1))

# Rearrange the cols to have the meta data in front
cols = df.columns.to_list()
df = df[cols[-6:] + cols[:-6]] # Move last 6 cols to the front

df.to_csv(csv_out, index=False)
