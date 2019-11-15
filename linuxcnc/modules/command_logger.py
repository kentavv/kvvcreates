#!/usr/bin/env python

from __future__ import print_function

import time

import linuxcnc

s = linuxcnc.stat()

while True:
    print(time.time(), s.command, sep='\t')
    time.sleep(.5)
