"""Sound-related stuff."""

from sound_lib.output import Output
output = Output()

old_stream = None
new_stream = None


def play(stream):
    """Play a stream."""
    global old_stream, new_stream
    old_stream = new_stream
    new_stream = stream
    new_stream.play()
