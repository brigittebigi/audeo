#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Brigitte Bigi
# Utility functions for videos.
# Required: ffmpeg
# ffmpeg needs to be built with the --enable-gpl --enable-libx265 
# configuration flag and requires x265 to be installed on your system.


from .utils import run_command

# ----------------------------------------------------------------------------


def extract_audio(video, audio):
    """Extract the audio of the video and re-encode into wav.

    :param video: (str) Input video file name
    :param audio: (str) Output audio file name
    
    """
    command = "ffmpeg "
    command += "-i '{:s}' ".format(video)
    command += "-vn -acodec pcm_s16le "
    command += "'{:s}' ".format(audio)
    command += "-nostdin -y"   # override if existing
    run_command(command)

# ----------------------------------------------------------------------------


def remove_audio_of_video(video, video_out):
    """Remove the audio of the given video.

    :param video: (str) Input filename of the video 
    :param video_out: (str) Output filename of the video

    """
    command = "ffmpeg -i '{:s}' ".format(video)
    command += "-c:v copy "
    command += "-an '{:s}' -hide_banner ".format(video_out)
    command += "-nostdin -y"   # override if existing
    run_command(command)

# ----------------------------------------------------------------------------


def add_audio_to_video(video, audio, video_out):
    """Add the audio to the given video.

    :param video: (str) Input filename of the video 
    :param audio: (str) Input audio file name
    :param video_out: (str) Output filename of the video

    Video stream is copied.
    Audio is converted to AAC, a lossy file format but WAV is not compatible
    with the video container.

    """
    command = "ffmpeg "
    command += "-i '{:s}' ".format(video)
    command += "-i '{:s}' ".format(audio)
    command += "-c:v copy "
    command += "-c:a aac -strict -2 "
    command += "'{:s}' ".format(video_out)
    command += "-nostdin -y"   # override if existing
    run_command(command)

# ----------------------------------------------------------------------------


def mult_fps_video(video, fps, video_out):
    """Modify the frame-per-seconds rate of the video.

    :param video: (str) Input filename of the video 
    :param fps: (int) Expected framerate (expected 15-100)
    :param video_out: (str) Output filename of the video (expect a .mkv)

    A re-encoding is required. No compression rate applied.
    Audio is removed of the video (if it was existing).
    
    """
    fps = int(fps)
    command = "ffmpeg "
    command += "-i '{:s}' ".format(video)
    command += "-f matroska "
    command += "-filter:v fps=fps={:d} ".format(fps)
    command += "-vcodec libx265 "
    command += "-crf 0 "
    command += "-pix_fmt yuv420p "
    command += "-an {:s} ".format(video_out)
    command += "-nostdin -y"
    run_command(command)

# ----------------------------------------------------------------------------


def trim_video_at_frame(video, from_time, from_frame, to_frame, video_out):
    """Trim a video with the highest precision as possible.

    :param video: (str) Input filename of the video 
    :param from_time: (str) Time position to start to trim
    :param from_frame: (int) Frame position to start to trim
    :param to_frame: (int) Frame position to end to trim
    :param video_out: (str) Output filename of the video (expect a .mkv)

    A re-encoding is required. No compression rate applied.
    
    """
    command = "ffmpeg "
    command += "-i '{:s}' ".format(video)
    command += "-f matroska "
    command += "-ss {:s} ".format(from_time)
    command += "-vf trim=start_frame={:d}:end_frame={:d} ".format(from_frame, to_frame)
    command += "-vcodec libx265 "
    command += "-crf 0 "
    command += "-pix_fmt yuv420p "
    command += "-an {:s} ".format(video_out)
    command += "-nostdin -y"
    run_command(command)

# ----------------------------------------------------------------------------


def convert_to_mpegts(video, video_out):
    """Convert the video to mpegts.

    :param video: (str) Input filename of the video 
    :param video_out: (str) Output filename of the video
    
    """    
    command = "ffmpeg "
    command += "-i '{:s}' ".format(video)
    command += "-c copy "
    command += "-bsf:v h264_mp4toannexb -f mpegts "
    command += "{:s}".format(video_out)
    run_command(command)

# ----------------------------------------------------------------------------


def concat_mpegts_to_video(videos, video_out):
    """Concatenate mpegts files to create a mp4 video.

    :param videos: (list) List of mpegts video files
    :param video_out: (str) Output filename of the video

    """
    mpegts = "|".join(videos)
    command = "ffmpeg "
    command += "-i 'concat:{:s}' ".format(mpegts)
    command += "-c copy "
    command += "{:s}".format(video_out)
    run_command(command)

# ----------------------------------------------------------------------------


def merge_video_audio(video, audio, video_out):
    """Merge audio and video without re-encoding.

    :param video: (str) Input filename of the video 
    :param audio: (str) Input filename of the audio
    :param video_out: (str) Output filename of the video (expect a .mkv)

    """
    command = "ffmpeg "
    command += "-i '{:s}' ".format(video)
    command += "-i '{:s}' ".format(audio)
    command += "-c:v copy "
    command += "-c:a copy "
    command += "'{:s}' -hide_banner ".format(video_out)
    command += "-nostdin -y"   # override if existing
    run_command(command)

# ----------------------------------------------------------------------------


def merge_and_compress(video, audio, video_out, crf=18):
    """Merge audio and video and convert to the MP4 lossy file format.

    :param video: (str) Input filename of the video 
    :param audio: (str) Input filename of the audio
    :param video_out: (str) Output filename of the video (expect a .mp4)
    :param crf: (int) Compression rate between 0 and 51.

    crf: 0=lossless / 18=visual lossless / 23=default / 51=worse 
    Notice that 0 (no compression) is not supported by H264.

    Video stream is converted to H264.
    Audio is converted to AAC.

    """
    command = "ffmpeg "
    command += "-i '{:s}' ".format(video)
    if audio is not None:
        command += "-i '{:s}' ".format(audio)
    command += "-f mp4 "
    command += "-vcodec libx264 "
    command += "-crf {:d} ".format(crf)
    command += "-preset slow "    # to keep a good quality
    command += "-profile:v main "
    command += "-pix_fmt yuv420p "
    command += "-c:a aac -strict -2 "
    command += "'{:s}' -hide_banner ".format(video_out)
    command += "-nostdin -y"   # override if existing
    run_command(command)

