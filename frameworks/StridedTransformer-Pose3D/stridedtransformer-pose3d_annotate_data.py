"""
===================================================================
Title:          stridedtransformer-pose3d_annotate_data.py
Description:    Merge output files to a single CSV file per video
Author:         Fabian Kahl
===================================================================
"""

import argparse
import pandas as pd
import cv2
import os
from numpy import load

parser = argparse.ArgumentParser()
parser.add_argument('-npz', '--npz_location', type=str, help='filepath of .npz file with the keypoint data')
parser.add_argument('-v', '--video', type=str, help='filepath of video')
parser.add_argument('-time', '--duration_location', type=str, help='filepath of duration measurement data')
parser.add_argument('-out', '--csv_out', type=str, help='output directory and name path for csv output')
args = parser.parse_args()

npz, duration_file, video, csv_out = args.npz_location, args.duration_location, args.video, args.csv_out

data = load(npz)
original_shape = data['reconstruction'].shape

# Column names
# Source: https://github.com/Vegetebird/MHFormer/issues/104
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

vid_name_in = os.path.basename(video)
vid_in_split = vid_name_in.split('_')
csv_name_out = vid_name_in.replace('.mp4', '.csv')

df = pd.DataFrame(data['reconstruction'].reshape(original_shape[0], -1), columns=cols)

# Fill some meta data
df['Subject'] = 'Sub'+str(int(vid_in_split[0]))
df['exerciseName'] = vid_in_split[2]
df['ipad_view'] = vid_in_split[3].split('.')[0]
df['duration'] = float(open(duration_file, 'r').read())

# To get timestamps
timestamps = []
cap = cv2.VideoCapture(video)
while cap.isOpened():
    success, _ = cap.read()
    if not success:
        print("Ignoring empty video frame.")
        break
    timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))
cap.release()
df['Timestamp'] = timestamps
df['Frame'] = list(range(1, len(df) + 1))

# Rearranges columns to have the meta data in front
cols = df.columns.to_list()
df = df[cols[-6:] + cols[:-6]] # Move last 6 cols to the front

df.to_csv(csv_out, index=False)