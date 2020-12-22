#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Brigitte Bigi
# Dependencies: ffmpeg
# Brief: Extract the audio of a video and convert to wav
# Usage: python audio_extract.py -v myvideo -o audio.wav 2> log

import sys
import os
from argparse import ArgumentParser

from src.ffmpeg_video import extract_audio

# ----------------------------------------------------------------------------

PROGRAM = os.path.abspath(__file__)
parser = ArgumentParser(usage="%s [options]" % os.path.basename(PROGRAM),
                        description="... a script to extract audio of a video.")

parser.add_argument("-v",
                    metavar="file",
                    required=True,
                    help='Input video file name.')

parser.add_argument("-o",
                    metavar="file",
                    required=False,
                    default="audio.wav",
                    help='Output audio file name.')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if os.path.exists(args.o) is True:
    print("A file with name {:s} is already existing.".format(args.o))
    sys.exit(1)

print("Extract audio of {:s}".format(args.v))
extract_audio(args.v, args.o)

if os.path.exists(args.o) is False:
    print("Process halted with error. Missing file {:s}.".format(fn))
    sys.exit(1)
else:
    print("File {:s} created successfully.".format(args.o))


