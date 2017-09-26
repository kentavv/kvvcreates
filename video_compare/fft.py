#!/usr/bin/env python3

import numpy as np
import pandas as pd


dat = pd.read_csv('t.csv', sep='\t')
n = dat.shape[0]

A = np.fft.rfft(dat['msum_bottom'], n)

amp_spec = np.abs(A)
pow_spec = amp_spec**2
phase_spec = np.angle(A)

dt = 1. / (2999.4 / 2)
tt = n * dt

header = ['index', 'freq', 'amp_spec', 'pow_spec', 'phase_spec']
print('\t'.join(header))
for i in range(n // 2 + 1):
    freq = i * 1. / tt
    #print(A[i])
    print('{0:4d}\t{1:.2f}\t{2:.2f}\t{3:.2f}\t{4:.2f}'.format(i, freq, amp_spec[i], pow_spec[i], phase_spec[i]))
