"""Sound-related stuff."""

import logging
from time import time
import wx
from sound_lib.output import Output
from attr import attrs, attrib
from .jobs import add_job
from . import app

logger = logging.getLogger(__name__)
last_run = 0
run_every = 0.1
zeroed = False


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


def update_ui():
    """Update user interface components."""
    global zeroed
    if not new_stream:
        state = None
        if not zeroed:
            zeroed = True
            app.frame.left_panel.position.SetValue(0)
    else:
        stream = new_stream.stream
        if stream.is_playing:
            state = 'Playing'
        elif stream.is_paused:
            state = 'Paused'
        elif stream.is_stopped:
            state = 'Stopped'
        app.frame.left_panel.position.SetValue(
            100 / stream.get_length() * stream.position
        )
    title = app.name
    if state is not None:
        title = '%s [%s]' % (title, state)
    app.frame.SetTitle(title)


def play_manager():
    """A job to check the status of playing streams and play the next one if
    the old one has finished."""
    global last_run
    now = time()
    if now - last_run >= run_every:
        last_run = now
        wx.CallAfter(update_ui)
    if new_stream is not None:
        if new_stream.stream.position >= new_stream.stream.get_length():
            # new_stream has finished. Let's get a new track from the queue.
            if queue:
                track = queue.pop(0)
                play(track)


add_job('Play Manager', play_manager)


def play(track):
    """Play a track."""
    global new_stream
    logger.info('Playing %r.', track)
    if new_stream is not None:
        played.append(old_stream)
        logger.info('Played: %r.', old_stream)
        if new_stream.stream.is_playing:
            new_stream.stream.pause()
    stream = track.get_stream()
    new_stream = Playing(track, stream)
    new_stream.stream.play()
