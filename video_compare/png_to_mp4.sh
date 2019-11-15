#!/bin/bash

ffmpeg -nostdin -r 30 -f image2 -s 1280x720 -i diff%04d.png -vcodec libx264 -crf 8 -pix_fmt yuv420p -preset veryslow -tune stillimage movie.mp4 &> ffmpeg.log &

