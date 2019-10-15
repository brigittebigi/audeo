How to create a corpus from the recordings?
Brigitte Bigi
October, 2019

Audeo is a library and scripts written in Python to synchronize an
audio with a video.


The recordings are supposed to be:
    - audio0: an high quality audio WAV file with 1 or 2 channels
    - video1: a video file including an audio stream
    - video2: a video file including an audio stream (optional)
It is required that a CLAP (or any other sound indicator) can be clearly
eared in all 3 audio streams.

Required: 
    - praat or audacity
    - ffmpeg <https://ffmpeg.org>
    - sox <http://sox.sourceforge.net>
    - sppas <http://www.sppas.org>
    - SPPAS environment variable.

Time values are given in the format HH:MM:SS.mmm or MM:SS.mmm:
   - 00:02:59 is representing 2 minutes and 59 seconds
   - 02:59.010 is 2 minutes, 29 seconds and 10 milliseconds


Step 1: Extract the 2 audios from the 2 videos
===============================================

> python audio_extract.py -v video1 -o audio1.wav 
> python audio_extract.py -v video2 -o audio2.wav


Step 2: Search for the clap in audio files
===========================================

Open all the 3 audio files with Audacity or Praat. 
In each audio file, search for the clap time value and zoom in to see where 
it exactly starts. 
Get all 3 time values (time0, time1, time2), rounded at 1ms.
audio1.wav and audio2.wav can be removed.


Step 3: Embed the audio into the videos
========================================

Use the script 'embed_audio_in_video.py' to synchronize and merge an audio with
a video. Options are:
   
    -a for the audio file name.
    -c for the time of the clap in this audio file.
    -v for the video file name. 
    -s for the time of the clap in this video file.
    -w for the directory in which to save result.
    -d to indicate the duration of the outputs (audio and the video).
    -C to select an audio channel.
    -P audio|video to set a priority for the synchronization
    --mkv to create a lossless audio/video file.
    --mp4 to create a lossy audio/video file.

Example of use:

> python embed_audio_in_video.py 
		-a audio0
		-c time0
		-v video1
		-s time1
		-w output1 
        -C left
	2> log1

> python embed_audio_in_video.py 
		-a audio0.wav 
		-c time0
		-v video2
		-s time2
		-w tmp2
        -C right
	2> log2

In each "output" directory, there are:
	- a file "audio_sync.wav";
	- a file "video_ssync.mov";
	- a file "merged_lossy.mp4" (if enabled);
    - a file "merged_lossless.mkv" (if enabled).

It has to be noticed that the MP4 is a lossy file format: the video is 
compressed with CRF=18, a low compression rate for an high video quality,
and the audio is compressed in aac format.

Example of use:

> python embed_audio_in_video.py -a ../samples/audio0.wav -c 00:07.469 -v ../samples/video0.MXF -s 00:07.640 -d 02:56 -w samples-left -C right -P video 2> log
> python embed_audio_in_video.py -a ../samples/audio0.wav -c 00:07.469 -v ../samples/video1.MTS -s 00:02.790 -d 02:56 -w samples-right -C left -P video 2> log

Finally, save the output stream of these scripts into a file.
It's important to remember the delta and all time values.
For video0, the clap of the newly embedded audio occurs 14 ms later than
the original one and in video1, it occurs 10ms before.

