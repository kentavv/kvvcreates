#!/usr/bin/env python3

import sys
import cv2
import numpy as np


if len(sys.argv) != 3:
    print('usage: {0:s} <grey, color> <video filename>'.format(sys.argv[0]))
    sys.exit(1)

mode = sys.argv[1]
fn = sys.argv[2]

if mode not in ['grey', 'color']:
    print('Unknown mode')
    sys.exit(1)

vid = cv2.VideoCapture(fn)
rv, img = vid.read()

frame_ind = 0

header = ['top', 'bottom']
if mode == 'color':
    header += ['top_blue', 'top_green', 'top_red']

header = ['frame'] + list(map(lambda x: 'med_' + x, header) )+ list(map(lambda x: 'msum_' + x, header) )
print(','.join(header))

while rv:
    h = img.shape[0]

    img_a = img[:h//2, :]
    img_b = img[h//2:, :]

    imgs = [img_a, img_b]
    if mode == 'color':
        imgs += [img_a[:, :, i] for i in range(3)]
    #else:
    #    imgs = list(map(lambda img: img[:, :, 0], imgs))

    meds = list(map(lambda img: np.median(img), imgs))
    sums = list(map(lambda img: np.sum(img) / 1e6, imgs))
    print(','.join(list(map(str, [frame_ind] + meds + sums))))

    rv, img = vid.read()
    frame_ind += 1
