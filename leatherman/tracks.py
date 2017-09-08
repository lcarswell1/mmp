"""Provides the Track class."""

from attr import attrs, attrib, Factory


@attrs
class Track:
    """A single track which can be played."""

    artist = attrib()
    album = attrib()
    title = attrib()
    meta = attrib(default=Factory(dict))

    def play(self):
        """Play the track."""
        raise NotImplementedError('You must implement this method yourself.')
