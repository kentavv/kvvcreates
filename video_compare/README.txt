These files are associated with the YouTube video: https://www.youtube.com/watch?v=QAR493e84Zg

They were used to examine the frame-by-frame difference between an original video and the one downloaded from YouTube.

The core program is compare_videos.py. If using it to compare an original to a YouTube video, first check the number of frames in each video. In the test case, the YouTube video had an extra frame. To be thorough, try various values for frame-skip with compare_videos.py and then examine the reported value of differences per frame for each configuration of frame-skip. Select the value for frame-skip that minimizes the difference.

The fft.py file was used measure the 60Hz flicker of AC lights captured by a high speed camera.
