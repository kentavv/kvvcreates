#!/bin/bash

fn1='compare_30fps_32Mbps.mp4'
fn2='compare_30fps_32Mbps_youtube.mp4'

for i in 0_0 0_1 0_2 0_3 0_4 1_0 2_0 3_0 4_0
do
  mkdir $i && pushd $i
  a=`echo $i | cut -d_ -f1`
  b=`echo $i | cut -d_ -f2`
  ../compare_videos.py $a $b $fn1 $fn2 &> log &
  popd
done

