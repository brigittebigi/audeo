#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Brigitte Bigi
# Utility functions

import sys
import os
import shlex
import subprocess

# ----------------------------------------------------------------------------


def file_exists(fn):
    """Exit because a file was not created or do nothing.

    Exit also if the file is empty.

    :param fn: (str) Name of the file to check

    """
    if os.path.exists(fn) is False:
        print("Process is halted. Missing file {:s}.".format(fn))
        sys.exit(1)
    if os.path.getsize(fn) == 0:
        print("Process is halted. Empty file {:s}.".format(fn))
        sys.exit(1)
    print("[  OK  ] {:s}".format(fn))

# ----------------------------------------------------------------------------


def print_step(nb, message=""):
    """Print a header step message.

    :param nb: (int) Step number
    :param message: (str) Step title
    
    """
    space = " "*((60-len(message))//2)
    msg = "STEP {:d}: {:s}".format(nb, message)
    print("")
    print("----------------------------------------------------------------")
    print(space + msg)
    print("----------------------------------------------------------------")
    sys.stderr.write("\n\n\n{:s}{:s}\n\n".format(space, msg))

# ---------------------------------------------------------------------------


def time_to_seconds(strtime):
    """Convert a time in string format into a number of seconds.
    
    Examples:

        >>>print(time_to_seconds("00:01"))
        >>>1.0
        >>>print(time_to_seconds("00:00:01.1"))
        >>>1.1
        >>>print(time_to_seconds("00:01:01"))
        >>>61.0
        >>>print(time_to_seconds("01:01:01"))
        >>>3661.0

    :param strtime: (str) String representing a time value (HH:MM:SS or MM:SS or MM:SS.m)
    :return: (float) Time in seconds

    """
    values = strtime.split(':')
    v = 0.
    if len(values) > 3 or len(values) == 1:
        raise ValueError('Time format not supported. Expected HH:MM:SS or MM:SS')
    elif len(values) == 3:
        # hours are given.
        v = float(values[0]) * 60. * 60.
        v += float(values[1]) * 60.
        v += float(values[2])
    else:
        v += float(values[0]) * 60.
        v += float(values[1])

    return v

# ---------------------------------------------------------------------------


def seconds_to_time(value):
    """Convert a number of seconds into a time in string format.
    
    Examples:

    >>>print(seconds_to_time(1.))
    >>>"00:01"
    >>>print(seconds_to_time(61.))
    >>>"01:01"
    >>>print(seconds_to_time(3661.234))
    >>>01:01:01.234

    :param value: (float) Time value in seconds
    :return: (str) String representing a time value (HH:MM:SS or MM:SS or MM:SS.m)

    """
    strtime = ""
    hours = int(float(value) // 3600)
    if hours > 0:
        strtime += "{:02d}:".format(hours)
    value -= (hours*3600)

    minutes = int(float(value) // 60)
    strtime += "{:02d}:".format(minutes)

    seconds = int(value % 60)
    strtime += "{:02d}".format(seconds)

    milliseconds = int((value %1) * 1000.)
    if milliseconds > 0:
        strtime += ".{:03d}".format(milliseconds)

    return strtime

# ---------------------------------------------------------------------------


def test_command(command):
    """Test if a command is available.

    :param command: (str) The command to execute as a sub-process.

    """
    NULL = open(os.path.devnull, "w")
    try:
        subprocess.call([command], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        NULL.close()
        return False

    NULL.close()
    return True

# ----------------------------------------------------------------------------


def run_command(command):
    """Execute a command is available.

    :param command: (str) The command to execute as a sub-process.

    """
    print("Run command:")
    print(command)
    command_args = shlex.split(command)
    p = subprocess.Popen(
        command_args, 
        shell=False, 
        stdout=subprocess.PIPE, 
        stderr=None
        )
    output = p.communicate()
    message = list()
    for m in output:
        if m is not None:
            message.append(m)
        if len(message) > 0:
            return message

    print("Done.")
