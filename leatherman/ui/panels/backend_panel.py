"""Provides the BackendPanel class."""

import logging
import wx
from wx.lib.sized_controls import SizedPanel
from attr import asdict
from ... import app, sound
from ...hotkeys import add_hotkey

logger = logging.getLogger(__name__)


class BackendPanel(SizedPanel):
    """The default panel used by Backend instances."""

    def __init__(self, backend, *args, **kwargs):
        """Initialise an add some controls."""
        self.backend = backend
        super(BackendPanel, self).__init__(*args, **kwargs)
        self.SetSizerType('form')
        self.search_label = wx.StaticText(self, label='&Search')
        self.search_field = wx.TextCtrl(self)
        add_hotkey(wx.WXK_RETURN, self.on_search, control=self.search_field)
        self.results_label = wx.StaticText(self, label='&Results')
        self.results = wx.ListBox(self)
        add_hotkey(
            wx.WXK_RETURN, self.on_activate, control=self.results
        )

    def on_search(self, event):
        """The enter key was pressed in the search field."""
        text = self.search_field.GetValue()
        logger.debug('Search: %s.', text)
        try:
            if self.backend.on_search(text):
                self.search_field.Clear()
        except Exception as e:
            self.backend.frame.on_error(e)

    def add_result(self, track):
        """Adds a Track instance to self.results."""
        res = self.results.Append(
            app.frame.track_format_template.render(**asdict(track))
        )
        self.results.SetClientData(res, track)
        return res

    def add_results(self, results, clear=True):
        """Add multiple results to self.results."""
        if clear:
            self.results.Clear()
        for result in results:
            self.add_result(result)
        self.results.SetFocus()
        if results:
            self.results.SetSelection(0)

    def get_result(self):
        """Get and return the currently-selected result."""
        i = self.results.GetSelection()
        if i >= 0:
            return self.results.GetClientData(i)

    def on_activate(self, event):
        """An entry in self.results has been clicked."""
        res = self.get_result()
        if res is not None:
            logger.info('Playing %r.', res)
            sound.play(res)
        else:
            wx.Bell()
