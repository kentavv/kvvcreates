#!/usr/bin/env python3

import sys
import cv2
import numpy as np


for fn in sys.argv[1:]:
    v = cv2.VideoCapture(fn)

    n = 0

    while v.read()[0]:
        n += 1

    print(fn, n, flush=True)
