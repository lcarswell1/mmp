"""Provides the BackendPanel class."""

import logging
from functools import partial
import wx
from wx.lib.sized_controls import SizedPanel
from attr import asdict
from ... import app, sound
from ...hotkeys import add_hotkey
from ...jobs import add_job

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

    def do_search(self, text):
        """This method will be called as a job to gather the results from
        self.backend.on_search and pass them to self.add_results."""
        results = self.backend.on_search(text)

        def finalise_search():
            """Add the results and clear the text field."""
            self.search_field.Clear()
            self.add_results(results)

        if results:
            wx.CallAfter(finalise_search)

    def on_search(self, event):
        """The enter key was pressed in the search field."""
        text = self.search_field.GetValue()
        logger.debug('Search: %s.', text)
        add_job(
            'Add results from %s' % self.backend.name,
            partial(self.do_search, text), one_shot=True
        )

    def add_result(self, track):
        """Adds a Track instance to self.results."""
        res = self.results.Append(
            app.frame.track_format_template.render(
                **asdict(track), backend=self.backend
            )
        )
        self.results.SetClientData(res, track)
        if not res:
            self.results.SetFocus()
            self.results.SetSelection(0)
        return res

    def add_results(self, results, clear=True):
        """Add multiple results to self.results."""
        if clear:
            self.results.Clear()
        for result in results:
            add_job(
                'Add result',
                partial(wx.CallAfter, self.add_result, result),
                one_shot=True
            )

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
