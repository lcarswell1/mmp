"""The view menu."""

import wx
from ... import app
from ..lyrics_frame import LyricsFrame
from ...hotkeys import add_hotkey, add_section

interface_section_id = add_section('Interface')


class ViewMenu(wx.Menu):
    """The view menu."""
    name = '&View'

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super().__init__(*args, **kwargs)
        parent.Bind(
            wx.EVT_MENU, self.toggle_lyrics, self.Append(
                wx.ID_ANY, 'Show / Hide &Lyrics',
                'Show or hide the lyrics frame.'
            )
        )
        add_hotkey(
            'L', self.toggle_lyrics, modifiers=wx.ACCEL_CTRL | wx.ACCEL_SHIFT,
            section_id=interface_section_id
        )

    def toggle_lyrics(self, event):
        """Show / hide the lyrics frame."""
        if app.lyrics_frame is None:
            app.lyrics_frame = LyricsFrame(self.parent)
        if app.lyrics_frame.Shown:
            app.lyrics_frame.Close(True)
        else:
            app.lyrics_frame.Show(True)
