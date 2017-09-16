"""Sound-related stuff."""

import logging
from time import time
import wx
from sound_lib.main import BassError
from sound_lib.output import Output
from attr import attrs, attrib
from .jobs import add_job
from . import app

logger = logging.getLogger(__name__)
last_run = 0
run_every = 0.1
zeroed = False
title = None  # Old frame title.


@attrs
class Playing:
    """A playing stream."""

    track = attrib()
    stream = attrib()


output = Output()
played = []
queue = []
old_stream = None
new_stream = None


def get_length_position(stream):
    """Gets appropriate values for length and poaisiton."""
    try:
        l = stream.get_length()
    except BassError:
        l = 0
    try:
        p = stream.position
    except BassError:
        p = l
    return (l, p)


def update_ui():
    """Update user interface components."""
    global zeroed, title
    if not new_stream:
        if not zeroed:
            zeroed = True
            app.frame.left_panel.position.SetValue(0)
    else:
        stream = new_stream.stream
        length, position = get_length_position(stream)
        if length:
            app.frame.left_panel.position.SetValue(
                100 / length * position
            )
    new_title = app.title_template.render(
        playing=new_stream, app_name=app.name
    )
    if new_title != title:
        title = new_title
    app.frame.SetTitle(title)


def play_manager():
    """A job to check the status of playing streams and play the next one if
    the old one has finished."""
    global last_run, new_stream
    now = time()
    if now - last_run >= run_every:
        last_run = now
        wx.CallAfter(update_ui)
    if new_stream is not None:
        length, position = get_length_position(new_stream.stream)
        if length and position and position >= length:
            # new_stream has finished. Let's get a new track from the queue.
            logger.info('%d/%d.', position, length)
            if queue:
                track = queue.pop(0)
                play(track)
            else:
                new_stream = None


add_job('Play Manager', play_manager)


def play(track, mark_played=True):
    """Play a track. If mark_played evaluates to False the old track (if any)
    will not be added to the played list."""
    global new_stream
    logger.info('Playing %r.', track)
    if new_stream is not None:
        if mark_played:
            played.append(new_stream.track)
            logger.info('Played: %r.', old_stream)
        if new_stream.stream.is_playing:
            new_stream.stream.pause()
    stream = track.get_stream()
    new_stream = Playing(track, stream)
    new_stream.stream.play()
