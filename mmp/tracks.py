"""Provides the Track class."""

from attr import attrs, attrib, Factory


@attrs
class Track:
    """A single track which can be played."""

    artist = attrib()
    album = attrib()
    number = attrib()
    title = attrib()
    index = attrib(default=Factory(lambda: None), init=False)

    def get_artist_title(self):
        """Should be overridden if your track hasn't got an artist or title
        attribute set and you want it to work with the lyrics frame."""
        return (self.artist or '', self.title or '')

    def activate(self):
        """This method is called when tracks are clicked on. If it raises
        NotImplementedError then get_stream is tried to play the track. You can
        override this method to make tracks that load other tracks for
        example."""
        raise NotImplementedError

    def get_stream(self):
        """Return a stream which can be played."""
        raise NotImplementedError('You must implement this method yourself.')
