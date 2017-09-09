"""Sound-related stuff."""

from sound_lib.output import Output
from attr import attrs, attrib
from .jobs import add_job


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


def play_manager():
    """A job to check the status of playing streams and play the next one if
    the old one has finished."""
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
    if new_stream is not None:
        played.append(new_stream)
        if new_stream.stream.is_playing:
            new_stream.stream.pause()
    stream = track.get_stream()
    new_stream = Playing(track, stream)
    new_stream.stream.play()
