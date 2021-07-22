#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Brigitte Bigi
# Dependencies: ffmpeg, sox, sppas

# Authors notes:
# Times are given either as:
#   - %HH:%MM:%SS.ms, or
#   - in seconds
# For example, 2 minutes and 59 seconds and 300 ms can be:
#   - 00:02:59.3 or
#   - 179.3
# If audio is 48000Hz (1 frame = 0.000020833 seconds) and video is 25Hz 
# (1 frame = 0.040 seconds), then, during one frame of a video, there are 
# 1920 audio frames. During 1 millisecond, there are 48 frames in the audio.

import sys
import os
import shutil
from argparse import ArgumentParser

from src.utils import file_exists, print_step, time_to_seconds, seconds_to_time
from src.utils import test_command
from src.ffmpeg_video import extract_audio, trim_video_at_frame
from src.ffmpeg_video import merge_video_audio, merge_and_compress
from src.utils_audio import audio_duration, trim_audio, add_silence_to_audio
from src.utils_audio import test_audio, extract_channel

# ----------------------------------------------------------------------------


def check_command(name):
    """Test the command and exit if not available.
    
    :param name: (str) Command name

    """
    result = test_command(name)
    if result is False:
        print("'{:s}' is not a valid command of your system.".format(name))
        sys.exit(1)
    else:
        print("'{:s}' is ok.".format(name))

# ----------------------------------------------------------------------------


def create_working_dir(wk):
    """Create the working or exists.

    :param wk: (str) Directory name.

    """
    if os.path.exists(wk):
        print("The working directory {:s} is already existing.".format(wk))
        sys.exit(1)
    os.mkdir(wk)
    os.chmod(wk, 0o777)
    print("Working directory: {:s}".format(wk))
    return wk

# ----------------------------------------------------------------------------


def adjust_audio_at_clap(audio_in, audio_clap, expected_clap, audio_out):
    """Create an audio file starting at the appropriate clap position.

    :param audio_in: (str) Input audio file name
    :param audio_clap: (float) Time of the start clap in the audio 
    :param expected_clap: (float) Time of the start clap in the video
    :param audio_out: (str) Output audio file name

    """
    delta = expected_clap - audio_clap

    if delta == 0:
        shutil.copy(audio_in, audio_out)
        print("Already matching. Nothing to do.")

    elif delta < 0:
        # The expected clap is before the one of the audio
        print("Trim the beginning of the audio of {:f} seconds"
              "".format(-delta))
        trim_audio(audio_in, -delta, audio_out, begin=True)

    else:
        # The expected clap is after the one of the audio
        print("Add {:f} seconds of silence at the beginning of the audio"
              "".format(delta))
        add_silence_to_audio(audio_in, delta, audio_out, begin=True)

# ----------------------------------------------------------------------------


def audio_with_duration(audio_in, expected_duration, audio_out):
    """Create an audio file during the same than the other one.

    :param audio_in: (str) Input audio file name
    :param expected_duration: (str) The expected duration
    :param audio_out: (str) Output audio file name

    """
    # Get the current audio duration
    cur_dur = audio_duration(audio_in)
    print("Duration of the audio is {:f} seconds".format(cur_dur))

    # Make the difference
    delta = expected_duration - cur_dur

    if delta == 0:
        shutil.copy(audio_in, audio_out)
        print("Already matching. Nothing to do.")

    elif delta > 0:
        # The expected duration is higher than the one we already have.
        print("Add {:f} seconds of silence at the end of the audio"
              "".format(delta))
        add_silence_to_audio(audio_in, delta, audio_out, begin=False)

    else:
        # The expected duration is less than the one we already have.
        print("Trim the end of the audio of {:f} seconds"
              "".format(-delta))
        trim_audio(audio_in, -delta, audio_out, begin=False)


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

PROGRAM = os.path.abspath(__file__)
parser = ArgumentParser(usage="%s [options]" % os.path.basename(PROGRAM),
                        description="... a script to mix audio and videos.")

parser.add_argument(
    "-a",
    metavar="file",
    required=True,
    help='Input audio file name.')

parser.add_argument(
    "-c",
    metavar="time",
    required=False,
    default="0",
    help='Time of the start clap in the audio (default: 00:00).')

parser.add_argument(
    "-v",
    metavar="file",
    required=True,
    help='Input video file name.')

parser.add_argument(
    "-s",
    metavar="time",
    required=False,
    default="0",
    help='Time of the start clap in the video (default: 00:00).')

parser.add_argument(
    "-d",
    metavar="time",
    required=False,
    help='Duration of the output video.')

parser.add_argument(
    "-FPS",
    metavar="value",
    required=False,
    type=float,
    default=25,
    help='Frames per seconds of the video (default=25)')

parser.add_argument(
    "-w",
    metavar="folder",
    required=False,
    default="tmp",
    help='Working directory to store the resulting files (default: tmp)')

parser.add_argument(
    "-C",
    metavar="value",
    required=False,
    default="none",
    help='Audio channel left|right|none (default=none=keep original)')

parser.add_argument(
    "-P",
    metavar="str",
    required=False,
    default="audio",
    help='Priority to audio or to video (default: audio). When priority is '
         'given to audio, the given audio will be exactly time-synchronized '
         'with the existing audio of the video. Otherwise, when priority is '
         'given to the video, the clap of the audio will be time-aligned with '
         'the middle of the frame containing the clap of the video.')

parser.add_argument(
    "--mkv",
    action='store_true',
    help='Create a merged audio+video lossless file (H265+WAV).')

parser.add_argument(
    "--mp4",
    action='store_true',
    help='Create a merged audio+video lossly file (H264+AAC)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

step = 1

# ----------------------------------------------------------------------------
# Check and get things...
# ----------------------------------------------------------------------------
print_step(step, "Check given arguments")

# Test the commands this script will need and create the working dir
check_command("sox")
check_command("ffmpeg")
file_exists(args.a)
file_exists(args.v)
if args.P not in ('audio', 'video'):
    print("'{:s}' is not a valid value for argument -P.".format(args.P))
wk = create_working_dir(args.w)

# Test the given audio
input_audio = test_audio(args.a, wk)

# Test the given video
# TODO: GET fps FROM THE GIVEN VIDEO.
input_video = args.v
fname, input_video_ext = os.path.splitext(input_video)
input_video_ext = input_video_ext.lower()
input_video_fps = args.FPS
input_video_frame_dur = 1. / input_video_fps

# convert given times in float (time in seconds)
expected_duration = None
if args.d:
    if ":" in args.d:
        expected_duration = time_to_seconds(args.d)
    else:
        expected_duration = float(args.d)
    print("Given duration for the output video: {:.3f}".format(expected_duration))
if ":" in args.s:
    input_video_clap = time_to_seconds(args.s)
else:
    input_video_clap = float(args.s)
print("Given clap position in the input video: {:.3f} seconds"
      "".format(input_video_clap))
if ":" in args.c:
    input_audio_clap = time_to_seconds(args.c)
else:
    input_audio_clap = float(args.c)
print("Given clap position in the input audio: {:.3f} seconds"
      "".format(input_audio_clap))
step += 1

# ----------------------------------------------------------------------------
# STEP 1: Estimate time values to synchronize (start pos)
# ----------------------------------------------------------------------------
print_step(step, "Estimate begin time values to synchronize")

# get the frame in which the clap is occurring
clap_frame_pos = int(input_video_clap / input_video_frame_dur)
clap_frame_time = float(clap_frame_pos) * input_video_frame_dur
print("Estimated beginning of the frame with the clap: {:.3f} seconds"
      "".format(clap_frame_time))

# adjust the position of the clap in this frame but
# by default, keep the real value for the audio clap of the video
estimated_video_clap = input_video_clap
if args.P == "video":
    # the clap of the audio is forced to be at the middle of the frame in which
    # the clap is occurring
    estimated_video_clap = clap_frame_time + (input_video_frame_dur / 2.)
print("Estimated clap position for the output: {:.3f} seconds"
      "".format(estimated_video_clap))

# print more details about the synchronization...
print("* * * Delta among the real clap position in the video and the beginning "
      "of the first frame of the video = {:.3f} * * *"
      "".format(input_video_clap - clap_frame_time))
if estimated_video_clap != input_video_clap:
    print("* * * Audio is shifted at the middle of the frame in which the clap "
          "is occurring. This shifted position = {:.3f} * * *"
          "".format(estimated_video_clap - clap_frame_time))
step += 1

# ----------------------------------------------------------------------------
# STEP 2: Estimate time values to synchronize (end pos)
# ----------------------------------------------------------------------------
print_step(step, "Estimate end time value to synchronize")

print("Get the exact duration of the video:")
file_audiov = os.path.join(wk, "audio_from_video.wav")
extract_audio(input_video, file_audiov)
file_exists(file_audiov)
file_audiov = test_audio(file_audiov, wk)
video_dur = audio_duration(file_audiov)

if expected_duration is not None:
    # Cut the video at the given end frame
    # but given argument is the expected duration (end = clap + duration))
    real_end_time = input_video_clap + expected_duration
    print("Expected end time: {:.3f} seconds"
          "".format(real_end_time))
    end_frame_pos = int(round(real_end_time / input_video_frame_dur))
    end_frame_time = float(end_frame_pos) * input_video_frame_dur
    if end_frame_time > video_dur:
        print("Error: Given expected duration is too high. Expected end = "
              "{:.3f} is higher than the video duration.".format(end_frame_time))
        sys.exit(1)
else:
    # Cut at the end (actually do not cut!)
    end_frame_time = video_dur
    end_frame_pos = int(round(end_frame_time / input_video_frame_dur))

print("Estimated end time: {:.3f} seconds"
      "".format(end_frame_time))
step += 1

# ----------------------------------------------------------------------------
# Step 3: Shift the audio to the expected clap position
# ----------------------------------------------------------------------------
print_step(step, "Shift audio to expected clap position in the video")
file_audio_clap = os.path.join(wk, "audio_clap.wav")
adjust_audio_at_clap(
    input_audio,
    input_audio_clap,       # position of the clap in the audio file
    estimated_video_clap,   # expected position of the clap in the video
    file_audio_clap)
file_exists(file_audio_clap)
step += 1


# ----------------------------------------------------------------------------
# Step 4: Trim audio
# ----------------------------------------------------------------------------
print_step(step, "Trim audio")
file_audio_endtrim = os.path.join(wk, "audio_trim_end.wav")
file_audio_trim = os.path.join(wk, "audio_trim.wav")

print("  - expected end time: {:.3f}".format(end_frame_time))
audio_with_duration(file_audio_clap, end_frame_time, file_audio_endtrim)
file_exists(file_audio_endtrim)

print("  - expected start time: {:.3f}".format(clap_frame_time))
trim_audio(file_audio_endtrim, clap_frame_time, file_audio_trim)
file_exists(file_audio_trim)
step += 1


# ----------------------------------------------------------------------------
# Step 5: Mix audio channels
# ----------------------------------------------------------------------------
print_step(step, "Audio channels")
file_audio_final = os.path.join(wk, "audio_sync.wav")

if args.C in ['left', 'right']:
    print("Select audio channel: {:s}".format(args.C))
    c = 1
    if args.C == "right":
        c += 1
    extract_channel(file_audio_trim, c, file_audio_final)
else:
    print("Nothing to do.")
    shutil.copy2(file_audio_trim, file_audio_final)

file_exists(file_audio_final)
step += 1

# ----------------------------------------------------------------------------
# Step 6: Trim the video
# ----------------------------------------------------------------------------
print_step(step, "Trim video")
file_video_final = os.path.join(wk, "video_sync.mkv")

print("  - start frame: {:d}".format(clap_frame_pos))
print("  - end frame: {:d}".format(end_frame_pos))
trim_video_at_frame(input_video,
                    seconds_to_time(clap_frame_time),
                    clap_frame_pos,
                    end_frame_pos,
                    file_video_final)
file_exists(file_video_final)
print("  - video container: Mastroska")
print("  - video codec: libx265 (crf=0)")
print("  - no audio")
step += 1


# ----------------------------------------------------------------------------
# Embed the audio into the video
# ----------------------------------------------------------------------------

if args.mp4 is True:
    print_step(step, "Merge and compress video-audio")
    file_video_lossy = os.path.join(wk, "merged_lossy.mp4")
    print("Create a compressed video embedding a compressed audio (MP4): ")
    print("  - video container: H264")
    print("  - video codec: libx264 (crf=18)")
    print("  - audio code: aac")
    merge_and_compress(file_video_final,
                       file_audio_final,
                       file_video_lossy, crf=18)
    file_exists(file_video_lossy)
    step += 1

if args.mkv is True:
    print_step(step, "Merge video-audio")
    print("Create a video embedding the audio (MKV)")
    file_video_lossless = os.path.join(wk, "merged_lossless.mkv")
    merge_video_audio(file_video_final, file_audio_final, file_video_lossless)
    file_exists(file_video_lossless)
    step += 1


# ----------------------------------------------------------------------------
# Remove temporary files
# ----------------------------------------------------------------------------

os.remove(file_audio_clap)
os.remove(file_audio_endtrim)
os.remove(file_audio_trim)
os.remove(file_audiov)
