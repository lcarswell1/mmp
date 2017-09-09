"""Sound-related stuff."""

from sound_lib.output import Output
output = Output()

old_stream = None
new_stream = None


def play(stream):
    """Play a stream."""
    global new_stream
    if new_stream is not None:
        new_stream.pause()
    new_stream = stream
    new_stream.play()
