#!/usr/bin/env python3

import sys
import cv2
import numpy as np


# dnf install opencv-python3 python3-numpy gstreamer1-vaapi gstreamer1-libav gstreamer1-vaapi-devel


if len(sys.argv) != 5:
    print('usage:  {0:s} <video 1 skip frames> <video 2 skip frames> <video 1 filename> <video 2 filename>\n'
          'example {0:s} 0 1 compare_30fps_32Mbps.mp4 compare_30fps_32Mbps_youtube.mp4'.format(sys.argv[0]))
    sys.exit(1)

v_pre = [int(sys.argv[1]), int(sys.argv[2])]
fns = sys.argv[3:5]

res_template = 'diff{0:04d}.png'

diff_min = 2
diff_scale = 1
diff_offset = 128


v = list(map(cv2.VideoCapture, fns))
frame_ind = 0
rv = [None] * len(v)
img = [None] * len(v)

# for each video, read any pre-roll frames to ignore and then the first frame to compare
for i in range(len(v)):
    for j in range(v_pre[i] + 1):
        rv[i], img[i] = v[i].read()

header = ['frame', 'v1 frame', 'v2 frame', 'min_img_diff', 'max_img_diff', 'median_img_diff', 'mean_img_diff', 'mega_sum_abs_imgd']
print(','.join(header))

# while all videos still have frames to read...
while sum(rv) == len(v):
    # for each pixel, calculate the difference in each channel
    imgd = img[0].astype(float) - img[1].astype(float)

    row = [frame_ind, frame_ind + v_pre[0], frame_ind + v_pre[1], np.min(imgd), np.max(imgd), np.median(imgd), np.mean(imgd), np.abs(imgd).sum() / 1e6]
    print(','.join(list(map(str, row))), flush=True)

    # for each pixel, create a boolean matrix, true where channel values are identical
    ind = img[0] == img[1]
    # for each pixel, create a boolean matrix, true for identical pixels (pixels with no channel differences)
    ind = np.all(ind, 2)

    # for each pixel, create a boolean matrix, true where absolute channel differences are less than diff_min
    ind2 = np.abs(imgd) < diff_min

    # scale and offset the difference image to improve visibility
    imgd = imgd * diff_scale + diff_offset

    # clamp pixel channel values outside of the 8-bit range
    imgd[imgd < 0] = 0
    imgd[imgd > 255] = 255

    # set pixels without significant difference to black
    imgd[ind2] = 0
    # set unchanged pixels to black
    imgd[ind] = 0

    cv2.imwrite(res_template.format(frame_ind), imgd)

    # for each video, read next frame
    for i in range(len(v)):
        rv[i], img[i] = v[i].read()
    frame_ind += 1
