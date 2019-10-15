#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Brigitte Bigi
# Utility functions for audio
# Required: sox, sppas

import sys
import os

from .utils import run_command

sys.path.append(os.getenv("SPPAS"))
import sppas.src.audiodata.aio

# ----------------------------------------------------------------------------


def test_audio(audio, workdir):
    try:
        print("Test audio file: {:s}".format(audio))
        fa = sppas.src.audiodata.aio.open(audio)
        print("  - duration: {:.3f}".format(fa.get_duration()))
        print("  - framerate: {:d}".format(fa.get_framerate()))
        print("  - channels: {:d}".format(fa.get_nchannels()))
        print("  - bitrate: {:d}".format(fa.get_sampwidth()*8))
        fa.close()
        return audio
    except Exception as e:
        print("SPPAS was not able to read the audio file: {:s}. Try to convert "
              "it with sox.".format(str(e)))
        new_audio = os.path.join(workdir, "audio_converted.wav")
        if os.path.exists(new_audio):
            print("File {:s} already exists.".format(new_audio))
            sys.exit(1)
        command = "sox "
        command += "'{:s}' -b 16 ".format(audio)
        command += "{:s} ".format(new_audio)
        run_command(command)
        return new_audio
    
# ----------------------------------------------------------------------------


def audio_duration(audio):
    """Return the duration of the audio (wav).

    It corresponds to execute this command:
    sox audio -n stat 2>&1 | sed -n 's#^Length (seconds):[^0-9]*\([0-9.]*\)$#\1#p'

    :param audio: (str) Input audio file name
    :return: (float) Duration in seconds
    
    """
    try:
        fa = sppas.src.audiodata.aio.open(audio)
        d = fa.get_duration()
        fa.close()
    except Exception as e:
        print("SPPAS was not able to read the audio file: {:s}. ".format(str(e)))
        sys.exit(1)

    return d

# ----------------------------------------------------------------------------


def trim_audio(audio, duration, audio_out, begin=True):
    """Trim an audio file.

    :param audio: (str) Input audio file name
    :param duration: (float) Duration (in seconds) to trim
    :param audio_out: (str) Output audio file name
    :param begin: (bool) True to trim at the beginning, False to trim the end.
    
    """
    cur_dur = audio_duration(audio)
    trim_dur = cur_dur - duration
    if begin is True:
        trim_start = duration 
    else:
        trim_start = 0.

    command = "sox '{:s}' ".format(audio)
    command += "'{:s}' ".format(audio_out)
    command += "trim {:f} {:f} ".format(trim_start, trim_dur)
    run_command(command)

# ----------------------------------------------------------------------------


def trim_audio_from_to(audio, from_time, to_time, audio_out):
    """Trim an audio file from a time position to a time position.

    :param audio: (str) Input audio file name
    :param from_time: (float) From time (in seconds)
    :param to_time: (float) To time (in seconds)
    :param audio_out: (str) Output audio file name
    
    """
    trim_dur = to_time - from_time
    
    command = "sox '{:s}' ".format(audio)
    command += "'{:s}' ".format(audio_out)
    command += "trim {:f} {:f} ".format(from_time, trim_dur)
    run_command(command)

# ----------------------------------------------------------------------------


def add_silence_to_audio(audio, duration, audio_out, begin=True):
    """Add silence at the begin or the end of an audio file.

    :param audio: (str) Input audio file name
    :param duration: (float) Duration (in seconds) to insert
    :param audio_out: (str) Output audio file name
    :param begin: (bool) True to insert the silence at the beginning, False to append it.
    
    """
    fa = sppas.src.audiodata.aio.open(audio)

    # create a file with silence
    command = "sox -n "
    command += "-r {:d} ".format(fa.get_framerate())
    command += "-c {:d} ".format(fa.get_nchannels())
    command += "-b {:d} ".format(fa.get_sampwidth()*8)
    command += "silence.wav "
    command += "trim 0.0 {:f}".format(duration)
    fa.close()    
    run_command(command)

    # concatenate the silence and the audio (or the contrary)
    command = "sox "
    if begin is True:
        command += "silence.wav "
        command += "'{:s}' ".format(audio)
    else:
        command += "'{:s}' ".format(audio)
        command += "silence.wav "
    command += "'{:s}' ".format(audio_out)    
    run_command(command)
    os.remove("silence.wav")

# ----------------------------------------------------------------------------


def extract_channel(audio, c, audio_out):
    """Extract the channel of an audio file.

    :param audio: (str) Input audio file name
    :param c: (int) Channel numberi (1=left, 2=right)
    :param audio_out: (str) Output audio file name

    """
    command = "sox "
    command += "'{:s}' ".format(audio)
    command += "-c 1 "
    command += "'{:s}' ".format(audio_out)
    command += "remix {:d}".format(c)
    run_command(command)

# ----------------------------------------------------------------------------


def mix_channels(audio, audio_out):
    """Mix the 2 first channels of an audio file.

    :param audio: (str) Input audio file name
    :param audio_out: (str) Output audio file name

    """
    command = "sox "
    command += "'{:s}' ".format(audio)
    command += "'{:s}' ".format(audio_out)
    command += "remix 1,2"
    run_command(command)
