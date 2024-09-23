"""
===================================================================
Title:          metrabs_annotate_data.py
Description:    Merge output files to a single CSV file per video
Author:         Fabian Kahl
===================================================================
"""

import os
import sys
import argparse
import pandas as pd
import cv2
from numpy import load
from pathlib import Path
import tensorflow_hub as tfhub

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--video_filepath', type=str, help='video filepath')
parser.add_argument('-npy', '--npy_dirpath', type=str, help='npy dirpath')
parser.add_argument('-time', '--duration_location', type=str, help='dirpath of duration measurement data')
parser.add_argument('-out', '--csv_dir_out', type=str, help='output directory for csv output')
parser.add_argument('-m', '--model_filepath', type=str, default='./models/metrabs_eff2l_y4', help='model filepath')
parser.add_argument('-s', '--skeleton', type=str, default='smpl_24', help='skeleton selection, see https://github.com/isarandi/metrabs/blob/master/docs/API.md')
args = parser.parse_args()

video_filepath = args.video_filepath
npy_dirpath = args.npy_dirpath
duration_file = args.duration_location
csv_dir_out = args.csv_dir_out
model_path = args.model_filepath

model = tfhub.load(model_path)
skeleton = args.skeleton

joint_names = model.per_skeleton_joint_names[skeleton].numpy().astype(str)
joint_edges = model.per_skeleton_joint_edges[skeleton].numpy()

pathlist = Path(npy_dirpath).rglob('*.npy')

duration = float(open(duration_file, 'r').read())
j = 0
for path in pathlist:
    j+=1
df = pd.DataFrame()
for k in range(1, j+1):
    path = npy_dirpath+'/'+str(k)+'.npy'
    npy_file = load(path, allow_pickle=True).tolist()
    for i in range(0, npy_file.shape[0]):
        try:
            df_frame = pd.DataFrame(npy_file[i][0], columns=['X', 'Y', 'Z'], index=joint_names)
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
if not os.path.exists(csv_dir_out):
    os.mkdir(csv_dir_out)
df.to_csv(csv_dir_out + csv_name_out, index=False)
