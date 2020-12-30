#!/usr/bin/env python

from __future__ import print_function

import os
import time

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import scipy.ndimage
#plt.style.use('dark_background')

plt.rcParams.update({
    "lines.color": "white",
    "patch.edgecolor": "white",
    "text.color": "black",
    "axes.facecolor": "white",
    "axes.edgecolor": "lightgray",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "grid.color": "lightgray",
    "figure.facecolor": "black",
    "figure.edgecolor": "black",
    "savefig.facecolor": "black",
    "savefig.edgecolor": "black"})


plt.rcParams['toolbar'] = 'None' 

max_t = 10

fig, ax = plt.subplots(1, 1)
ax.set_xlim(0, max_t)
ax.set_ylim(0, 1000)
ax.hold(True)

plt.show(False)
plt.draw()

plt.axhspan(700, 1000, facecolor='r', alpha=0.05)
plt.axhspan(700/7.1*2.4, 700, facecolor='g', alpha=0.05)
plt.axhspan(0, 700/7.1*2.4, facecolor='b', alpha=0.05)

#for i in range(10):
#   y = np.random.random()
#   plt.scatter(i, y)
#   plt.pause(0.05)

#plt.show()

#ax.axhline(y=700)
# min_line = ax.axhline(y=0)
max_line = ax.axhline(y=0)
background = fig.canvas.copy_from_bbox(ax.bbox)

target_load = 400
kp = 2
ki = .002
kd = .5

max_i = 6

def follow(f):
    f.seek(0, os.SEEK_END)
    
    while True:
        ln = f.readline()
        if not ln:
            time.sleep(0.1)
        else:
            yield ln

f = open('dyn4.log')
f = follow(f)
x = []
y = []
y2 = []
y3 = []
y4 = []
# err_lst = []
p_err = None
term_p = 0
term_i = 0
term_d = 0
points = ax.plot(x, y, 'b+', animated=False)[0]
points2 = ax.plot(x, y2, 'g-', animated=False)[0]
points3 = ax.plot(x, y3, 'r-', animated=False)[0]
points4 = ax.plot(x, y4, 'y-', animated=False)[0]
d = [[0, 0]]
lt = 0
for ln in f:
    ln = ln.rstrip()

    try:
        t, pos, trq, en, trq_warning, adaptive_feed = ln.split(',')
    except ValueError:
        continue
    t = float(t)
    cur_t = t
    t = int(abs(t) * 1000 / 20)
    trq = float(trq) 
    en = en == '1'

    if t == d[-1][0]:
        d[-1][1] = max(d[-1][1], trq)
    else:
       d += [[t, trq]]
    
    d = [d_ for d_ in d if d[-1][0] - d_[0] <= max_t * 20]

    #cur_t = time.time()
    if cur_t - lt > .5:
        lt = cur_t

        x = [max_t - (d[-1][0] - d_[0]) / 20. for d_ in d]
        y = [d_[1] for d_ in d]

        # Calculate moving average using a uniform filter, with the center shifted
        # half of the window size.
        N = 21
        y2 = scipy.ndimage.uniform_filter1d(y, mode='nearest', size=N, origin=N//2)
        N = 5
        y3 = scipy.ndimage.maximum_filter1d(y, mode='nearest', size=N, origin=N//2)
        # y4 = scipy.ndimage.minimum_filter1d(y, mode='nearest', size=N, origin=N//2)

        if len(y2) >= 2:
            dt = y[-1] - y[-2]
            cur_load = y2[-1]
            err = cur_load - target_load
            # err_lst += [err]

            if p_err is not None:
                term_p = kp * err
                term_i += ki * dt * err
                term_d = kd * (err - p_err) / dt
                pid_i_raw = term_p + term_i + term_d
                pid_i = pid_i_raw
                if pid_i < -max_i:
                    pid_i = -max_i
                elif pid_i > max_i:
                    pid_i = max_i

                print(dt, cur_load, target_load, err, term_p, term_i, term_d, pid_i_raw, pid_i)

            p_err = err

        #print(x, y)
        points.set_data(x, y)
        #points2.set_data(x[4:], y2)
        points2.set_data(x, y2)
        points3.set_data(x, y3)
        # points4.set_data(x, y4)
        # min_line.set_ydata(np.amin(y))
        max_line.set_ydata(np.amax(y))
        if True:
            fig.canvas.draw()
        else:
            fig.canvas.restore_region(background)
            ax.draw_artist(points)
            fig.canvas.blit(ax.bbox)
        # plt.pause(0.02)
        print('draw')
        plt.pause(0.1)

        #print(t, trq, en)

