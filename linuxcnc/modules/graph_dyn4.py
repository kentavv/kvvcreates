#!/usr/bin/env python

from __future__ import print_function

import sys
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

max_t = 2

fig, ax = plt.subplots(1, 1)
ax.set_xlim(0, max_t)
ax.set_ylim(-1000, 1000)
ax.hold(True)
ax.set_ylabel('Load')
ax.set_xlabel('Time')

ax2 = ax.twinx()
ax2.set_xlim(0, max_t)
ax2.set_ylim(-.01, 1.01)
ax.hold(True)
ax2.set_ylabel('Adaptive feed')

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

fn = sys.argv[1]
st = 0
if fn == 'follow':
    fn = sys.argv[2]
    f = open(fn)
    f = follow(f)
    mode = 'follow'
elif fn == 'time':
    st = float(sys.argv[2])
    fn = sys.argv[3]
    f = open(fn)
    mode = 'playback'
else:
    f = open(fn)
x = []
y = []
y2 = []
y3 = []
y4 = []
y5 = []
# err_lst = []
p_err = None
term_p = 0
term_i = 0
term_d = 0
points = ax.plot(x, y, 'b+', animated=False)[0]
points2 = ax.plot(x, y2, 'g-', animated=False)[0]
points3 = ax.plot(x, y3, 'r-', animated=False)[0]
points4 = ax.plot(x, y4, 'y-', animated=False)[0]
points5 = ax2.plot(x, y5, 'y-', animated=False)[0]
d = [[0, 0]]
lt = 0
p_ti = time.time()
c_update = 0
lt_update = 0
first_t = None
first_draw = None
follow_skip = 0
follow_max_lag = .020

for ln_n, ln in enumerate(f):
    # if ln_n % 50 != 0:
    #     continue

    #if ln_n < 18000:
    #    continue
    #if ln_n < 9500:
    #    continue
    ln = ln.rstrip()
    # print(ln_n, ln)

    try:
        t, pos, trq, en, trq_warning, adaptive_feed = ln.split(',')
    except ValueError:
        continue
    t = float(t)
    if st is not None and t < st:
        continue

    if first_t is None:
        first_t = t

    c_ti = time.time()
    #print(c_ti - p_ti)
    p_ti = c_ti

    # When following, we skip lines until the log time is within range of
    # the current time.
    if mode == 'follow' and c_ti - t > follow_max_lag:
        follow_skip += 1
        continue

    cur_t = t
    #t = int(abs(t) * 1000 / 20)
    t = abs(t)
    trq = float(trq) 
    af = float(adaptive_feed) 
    en = en == '1'

    if t == d[-1][0]:
        d[-1][1] = max(d[-1][1], trq)
    else:
       d += [[t, trq, af]]
    
    d = [d_ for d_ in d if d[-1][0] - d_[0] <= max_t * 20]

    #cur_t = time.time()
    if cur_t - lt > .05:
        if mode == 'follow':
            up_dt = c_ti - t
            print('lag', up_dt, follow_skip)
            follow_skip = 0
        elif mode == 'playback':
            if first_draw is None:
                first_draw = time.time()
            else:
                # When playing back, all values are drawn, but drawing is about 4x slower than realtime
                lg_mult = 4
                lg_dt = cur_t - first_t
                up_dt = time.time() - first_draw
                w = lg_dt * lg_mult - up_dt
                if w > 0:
                    time.sleep(w)
                elif w < 0:
                    print('lag', ln_n, lg_dt, up_dt, lg_dt / up_dt, lg_dt * lg_mult, up_dt, w)

#        c_update = time.time()
#        dt_update1 = c_update - lt_update
#        dt_update2 = (cur_t - lt)*4 - dt_update1
#        print(c_update, lt_update, dt_update1, dt_update2)
#        if lt_update > 0 and dt_update2 > 0:
#            time.sleep(dt_update2)
#
#        lt_update = c_update

#        print(d)
        lt = cur_t

        #x = [max_t - (d[-1][0] - d_[0]) / 20. for d_ in d]
        x = [max_t - (d[-1][0] - d_[0]) for d_ in d]
        y = [d_[1] for d_ in d]
        y5 = [d_[2] for d_ in d]

        # Calculate moving average using a uniform filter, with the center shifted
        # half of the window size.
        N = 21
        #N = 311
        y2 = scipy.ndimage.uniform_filter1d(y, mode='nearest', size=N, origin=N//2)
        y3 = scipy.ndimage.uniform_filter1d(np.abs(y), mode='nearest', size=N, origin=N//2)
        N = 5
        #y3 = scipy.ndimage.maximum_filter1d(y, mode='nearest', size=N, origin=N//2)
        # y4 = scipy.ndimage.minimum_filter1d(y, mode='nearest', size=N, origin=N//2)

#        if len(y2) >= 2:
#            dt = y[-1] - y[-2]
#            cur_load = y2[-1]
#            err = cur_load - target_load
#            # err_lst += [err]
#
#            if p_err is not None:
#                term_p = kp * err
#                term_i += ki * dt * err
#                term_d = kd * (err - p_err) / dt
#                pid_i_raw = term_p + term_i + term_d
#                pid_i = pid_i_raw
#                if pid_i < -max_i:
#                    pid_i = -max_i
#                elif pid_i > max_i:
#                    pid_i = max_i
#
#                print(dt, cur_load, target_load, err, term_p, term_i, term_d, pid_i_raw, pid_i)
#
#            p_err = err

        #print(x, y)
        points.set_data(x, y)
        #points2.set_data(x[4:], y2)
        points2.set_data(x, y2)
        points3.set_data(x, y3)
        # points4.set_data(x, y4)
        points5.set_data(x, y5)
        # min_line.set_ydata(np.amin(y))
        max_line.set_ydata(np.amax(y))
        if True:
            fig.canvas.draw()
        else:
            fig.canvas.restore_region(background)
            ax.draw_artist(points)
            fig.canvas.blit(ax.bbox)
        plt.pause(0.005)
#        print('draw')
        # plt.pause(0.1)

        #print(t, trq, en)

plt.show()
