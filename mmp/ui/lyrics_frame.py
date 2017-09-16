"""The frame that lyrics should load into."""

import logging
import wx
from lyricscraper.lyrics import get_lyrics
from .. import app, sound
from ..jobs import add_job

logger = logging.getLogger(__name__)
nothing_playing = 'Nothing playing.'
lyrics_loading = 'Loading lyrics...'


class LyricsFrame(wx.Frame):
    """A frame to display lyrics."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('title', 'Lyrics')
        super().__init__(*args, **kwargs)
        self.artist = None
        self.title = None
        self._lyrics = 'Let update_lyrics sort this one out.'
        p = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        self.label = wx.StaticText(p, label='&Lyrics')
        s.Add(self.label, 0, wx.GROW)
        self.lyrics = wx.TextCtrl(p, style=wx.TE_MULTILINE | wx.TE_READONLY)
        s.Add(self.lyrics, 1, wx.GROW)
        p.SetSizerAndFit(s)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_SHOW, self.on_show)

    def on_close(self, event):
        app.lyrics_frame = None
        event.Skip()

    def on_show(self, event):
        """Maximize the frame too."""
        event.Skip()
        self.Maximize()

    def load_lyrics(self, artist, title):
        """Get the lyrics and update this frame."""
        old_artist = self.artist
        old_title = self.title
        self.artist = artist
        self.title = title
        if not artist or not title:
            if self._lyrics is not None:
                wx.CallAfter(self.lyrics.SetValue, nothing_playing)
                self._lyrics = None
                logger.info('Lyrics cleared.')
            return
        if artist == old_artist and title == old_title:
            return  # Nothing to do.
        wx.CallAfter(self.lyrics.SetValue, lyrics_loading)
        logger.info('Loading lyrics for %s - %s.', artist, title)
        lyrics = get_lyrics(artist, title)
        if lyrics is None:
            logger.info('Lyrics not found.')
            text = 'No lyrics found for %s - %s.' % (artist, title)
        else:
            logger.info('Lyrics object: %r.', lyrics)
            text = '%s - %s\nFrom: %s\n\n%s' % (
                artist, title, lyrics.engine, lyrics.lyrics.strip()
            )
        self._lyrics = text
        wx.CallAfter(self.lyrics.SetValue, text)


def update_lyrics():
    """A job to update the lyrics."""
    if app.lyrics_frame is None:
        return
    f = app.lyrics_frame
    if sound.new_stream is None:
        artist, title = ('', '')
    else:
        artist, title = sound.new_stream.track.get_artist_title()
    f.load_lyrics(artist, title)


add_job('Update Lyrics', update_lyrics, run_every=1.0)
