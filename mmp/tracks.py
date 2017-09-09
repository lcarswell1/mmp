"""Provides the Track class."""

from attr import attrs, attrib, Factory


@attrs
class Track:
    """A single track which can be played."""

    artist = attrib()
    album = attrib()
    number = attrib()
    title = attrib()
    meta = attrib(default=Factory(dict))

    def get_stream(self):
        """Return a stream which can be played."""
        raise NotImplementedError('You must implement this method yourself.')
