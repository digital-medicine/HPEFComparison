#!/usr/bin/env python
# coding: utf-8

# Changed
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import argparse
import numpy as np

import sys
import urllib.request
import tensorflow as tf
import tensorflow_hub as tfhub
import tensorflow_io as tfio
import cameralib

# Changed
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--video_filepath', type=str, help='video filepath')
parser.add_argument('-m', '--model_filepath', type=str, default='./models/metrabs_eff2l_y4', help='model filepath')
parser.add_argument('-s', '--skeleton', type=str, default='smpl_24', help='skeleton selection, see https://github.com/isarandi/metrabs/blob/master/docs/API.md')
parser.add_argument('-o', '--out_dirpath', type=str, help='npy output dir path')
args = parser.parse_args()

# Changed
model_path = args.model_filepath
skeleton = args.skeleton
video_filepath = args.video_filepath
dirpath_out = args.out_dirpath

# Changed
model = tfhub.load(model_path)

# Changed
if not os.path.exists(dirpath_out):
    os.mkdir(dirpath_out)

joint_names = model.per_skeleton_joint_names[skeleton].numpy().astype(str)
joint_edges = model.per_skeleton_joint_edges[skeleton].numpy()

frame_batches = tfio.IODataset.from_ffmpeg(video_filepath, 'v:0').batch(8).prefetch(1)

camera = cameralib.Camera.from_fov(
    fov_degrees=55, imshape=frame_batches.element_spec.shape[1:3])

# Changed
i = 0

for frame_batch in frame_batches:
    pred = model.detect_poses_batched(
            frame_batch, intrinsic_matrix=camera.intrinsic_matrix[tf.newaxis],
            skeleton=skeleton)

    # Changed
    i+=1
    np.save(dirpath_out+str(i)+'.npy', pred['poses3d'])