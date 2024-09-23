#!/usr/bin/env python
# coding: utf-8

# ##### Copyright 2023 The MediaPipe Authors. All Rights Reserved.

#mediapipe
#@title Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# # Pose Landmarks Detection with MediaPipe Tasks
# 
# This notebook shows you how to use MediaPipe Tasks Python API to detect pose landmarks from images.

# ## Visualization utilities

#@markdown To better demonstrate the Pose Landmarker API, we have created a set of visualization tools that will be used in this colab. These will draw the landmarks on a detect person, as well as the expected connections between those markers.

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np


def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)

  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]

    # Draw the pose landmarks.
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      pose_landmarks_proto,
      solutions.pose.POSE_CONNECTIONS,
      solutions.drawing_styles.get_default_pose_landmarks_style())
  return annotated_image

# Changed
# Source: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker
joint_names = ['nose',
'left eye (inner)',
'left eye',
'left eye (outer)',
'right eye (inner)',
'right eye',
'right eye (outer)',
'left ear',
'right ear',
'mouth (left)',
'mouth (right)',
'left shoulder',
'right shoulder',
'left elbow',
'right elbow',
'left wrist',
'right wrist',
'left pinky',
'right pinky',
'left index',
'right index',
'left thumb',
'right thumb',
'left hip',
'right hip',
'left knee',
'right knee',
'left ankle',
'right ankle',
'left heel',
'right heel',
'left foot index',
'right foot index']

# ## Running inference and visualizing the results
# 
# The final step is to run pose landmark detection on your selected image. This involves creating your PoseLandmarker object, loading your image, running detection, and finally, the optional step of displaying the image with visualizations.
# 
# Check out the [MediaPipe documentation](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python) to learn more about configuration options that this solution supports.
# 

# STEP 1: Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Changed
import cv2
import pandas as pd
import argparse
import os

# Changed
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--video_filepath', type=str, help='video filepath')
parser.add_argument('-m', '--model_filepath', type=str, default='./pose_landmarker_heavy.task', help='model filepath')
parser.add_argument('-o', '--csv_out_filepath', type=str, help='csv output filepath')
parser.add_argument('-oo', '--video_out_filepath', type=str, help='video output filepath')
args = parser.parse_args()

# Changed
video_path = args.video_filepath
model_path = args.model_filepath
filepath_out = args.csv_out_filepath
video_path_out = args.video_out_filepath

# Changed
os.makedirs(os.path.dirname(filepath_out), exist_ok=True)

# Changed
cap = cv2.VideoCapture(video_path)
cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap_fps = cap.get(cv2.CAP_PROP_FPS)
out = cv2.VideoWriter(video_path_out,
                      cv2.VideoWriter_fourcc(*"mp4v"), cap_fps, (cap_width,cap_height))

# STEP 2: Create an PoseLandmarker object.
# Changed
base_options = python.BaseOptions(model_asset_path=model_path)
VisionRunningMode = mp.tasks.vision.RunningMode
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True,
    running_mode=VisionRunningMode.VIDEO)
#detector = vision.PoseLandmarker.create_from_options(options)

#BaseOptions = mp.tasks.BaseOptions
#PoseLandmarker = mp.tasks.vision.PoseLandmarker
#PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
#VisionRunningMode = mp.tasks.vision.RunningMode

# Create a pose landmarker instance with the video mode:
#options = PoseLandmarkerOptions(
#    base_options=BaseOptions(model_asset_path=model_path),
#    running_mode=VisionRunningMode.VIDEO)

# Changed
df = pd.DataFrame()
missing_frames = 0
with vision.PoseLandmarker.create_from_options(options) as detector:
    while cap.isOpened():
        success, numpy_frame_from_opencv = cap.read()
        frame_timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        if not success:
            print("Ignoring empty video frame.")
            break

        # STEP 3: Load the input image.
        # Changed
        numpy_frame_from_opencv = cv2.cvtColor(numpy_frame_from_opencv, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_frame_from_opencv)

        # STEP 4: Detect pose landmarks from the input image.
        # Changed
        pose_landmarker_result = detector.detect_for_video(mp_image, frame_timestamp_ms)

        # STEP 5: Process the detection result. In this case, visualize it.
        annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), pose_landmarker_result)

        # Changed
        # writes the results in out
        out.write(cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))

        # Changed
        # Put data in 2D table
        try:
            table = []
            for i in pose_landmarker_result.pose_landmarks[0]:
                table.append([i.x, i.y, i.z, i.visibility])
            df_frame = pd.DataFrame(table, columns=['X', 'Y', 'Z', 'Visibility'], index=joint_names)

            # Changed
            # Stack rows on cols --> one row with "col_row"
            df_frame_stacked = df_frame.stack().to_frame()
            df_frame_stacked.set_index(df_frame_stacked.index.map(''.join), inplace=True)
            df_frame_stacked = df_frame_stacked.transpose()

            # Changed
            # Add meta data
            df_frame_stacked['Frame'] = cap.get(cv2.CAP_PROP_POS_FRAMES)
            df_frame_stacked['Timestamp'] = cap.get(cv2.CAP_PROP_POS_MSEC)
    
            # Changed
            # Rearrange the cols to have the meta data in front
            cols = df_frame_stacked.columns.to_list()
            df_frame_stacked = df_frame_stacked[cols[-2:] + cols[:-2]] #moves last 2 cols to the front

            # Changed
            # Append df_frame_stacked on df containing all frames
            df = pd.concat([df, df_frame_stacked])
        except:
            missing_frames+=1
            pass
cap.release()
out.release()

# Changed
df.to_csv(filepath_out, index=False)

# Changed
message = video_path+': '+str(missing_frames)+' of '+str(cap_length)+' frames are missing!'
print(message)