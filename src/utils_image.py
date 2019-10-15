#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Brigitte Bigi
# Utility functions for images.
# Required: ffmpeg, convert (ImageMagick)


from .utils import run_command

# ----------------------------------------------------------------------------

def create_image_with_text(text, image, size="1440x1080"):
    """Create an image with the given text in the middle.

    :param text: (str) A multiline text
    :param image: (str) PNG output image
    :param size: (str) Image size

    """
    command = "convert -alpha on "
    command += "-fill black "  # text color
    command += "-pointsize 60 "  # text size
    command += "-gravity center "  # center text
    command += "-strokewidth 2 "
    command += "-stroke black "
    command += "-undercolor lightblue "
    command += "-size {:s} ".format(size)  # image size
    command += "caption:'{:s}' ".format(text)
    command += "png32:{:s}".format(image)
    run_command(command)

# ----------------------------------------------------------------------------


def image_to_video(image, video, duration=5):
    """Create a video from a single image.

    :param image: (str) Input image file name
    :param video: (str) Output video file name (with extension .mp4)
    :param duratio: (int) Video duration (in seconds)

    """
    command = "ffmpeg "
    command += "-loop 1 "
    command += "-i {:s} ".format(image)
    command += "-c:v libx264 "
    command += "-t {:d} ".format(duration)
    command += "-pix_fmt yuv420p "
    command += "{:s}".format(video)
    run_command(command)
