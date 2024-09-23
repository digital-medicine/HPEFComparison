import time

import cv2

from rtmlib import Body, draw_skeleton

# Changed
from argparse import ArgumentParser
import os
import numpy as np

device = 'cpu'
backend = 'onnxruntime'  # opencv, onnxruntime, openvino

# Changed
parser = ArgumentParser()
parser.add_argument('--video-path', type=str, default='', help='Video path')
parser.add_argument('--out-video-root',
        type=str, default=None,
        help='Root of the output video file. '
        'Default not saving the visualization video.')
args = parser.parse_args()

# Changed
input_vid_path = args.video_path
output_vid_path = os.path.join(args.out_video_root, f'{os.path.basename(args.video_path)}')
os.makedirs(args.out_video_root+'/npy', exist_ok=True)

# Changed
cap = cv2.VideoCapture(input_vid_path)

# Changed
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Changed
out = cv2.VideoWriter(output_vid_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

openpose_skeleton = False  # True for openpose-style, False for mmpose-style

body = Body(
    pose='rtmo',
    to_openpose=openpose_skeleton,
    mode='performance',  # balanced, performance, lightweight
    backend=backend,
    device=device)

frame_idx = 0

# Changed
i = -1

while cap.isOpened():
    success, frame = cap.read()
    frame_idx += 1

    # Changed
    i += 1
    
    if not success:
        break
    s = time.time()
    keypoints, scores = body(frame)
    det_time = time.time() - s
    print('det: ', det_time)

    img_show = frame.copy()

    # if you want to use black background instead of original image,
    # img_show = np.zeros(img_show.shape, dtype=np.uint8)

    img_show = draw_skeleton(img_show,
                             keypoints,
                             scores,
                             openpose_skeleton=openpose_skeleton,
                             kpt_thr=0.3,
                             line_width=2)

    # Changed
    #img_show = cv2.resize(img_show, (960, 640))
    #cv2.imshow('img', img_show)
    out.write(img_show)
    np.save(args.out_video_root+'/npy/'+str(i)+'.npy', keypoints)
    cv2.waitKey(10)

# Changed
cap.release()
out.release()
cv2.destroyAllWindows()
