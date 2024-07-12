Script to synchronize videos before processing in Freemocap.

The method used to synchronize the videos is by detecting a high difference in brightness within consecutive frames of the video.
For best results, the brightness difference should be produced by turning on a lamp in front all of the cameras at the same time at the beginning of the recording.

The videos should be placed in a directory called "videos" inside the same folder as the script.

It can handle different video formats and orientations.

Some parameters can be adjusted in the main function.

Module requirements:
- OpenCV
- MoviePy
