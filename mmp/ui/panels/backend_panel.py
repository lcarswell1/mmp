"""Provides the BackendPanel class."""

import logging
from functools import partial
import wx
from wx.lib.sized_controls import SizedPanel
from attr import asdict
from ... import app, sound
from ...jobs import add_job

logger = logging.getLogger(__name__)


class BackendPanel(SizedPanel):
    """The default panel used by Backend instances."""

    def __init__(self, backend, *args, **kwargs):
        """Initialise an add some controls."""
        self.backend = backend
        super(BackendPanel, self).__init__(*args, **kwargs)
        self.menu = wx.Menu()
        self.play_menu_item = self.menu.Append(
            wx.NewId(), '&Play',
            'Play the track that is selected.'
        )
        self.Bind(wx.EVT_MENU, self.on_activate, self.play_menu_item)
        self.SetSizerType('form')
        self.search_label = wx.StaticText(self, label='&Find')
        self.search_field = wx.TextCtrl(self)
        self.results_label = wx.StaticText(self, label='&Results')
        self.results = wx.ListBox(self)
        self.results.Bind(wx.EVT_RIGHT_DOWN, self.on_context)

    def on_context(self, event):
        """Show the context menu self.menu."""
        if self.menu is None or (
            self.get_result() is None and self.results.HitTest(
                event.GetPosition()
            ) == -1
        ):
            return wx.Bell()
        self.results.PopupMenu(self.menu)

    def do_search(self, text, backend=None):
        """This method will be called as a job to gather the results from
        the on_search hook of the provided backend (or self.backend) and pass
        them to self.add_results."""
        if backend is None:
            backend = self.backend
        logger.debug('Searching %r for %s.', backend, text)
        results = backend.on_search(text)

        def finalise_search():
            """Add the results and clear the text field."""
            self.search_field.Clear()
            self.add_results(results, backend=backend)

        if results:
            wx.CallAfter(finalise_search)
        else:
            wx.CallAfter(
                self.backend.frame.on_error, 'No results found for %s.' % text
            )
        return True

    def on_search(self, event):
        """The enter key was pressed in the search field."""
        text = self.search_field.GetValue()
        add_job(
            'Add results from %s' % self.backend.name,
            partial(self.do_search, text)
        )

    def stringify(self, track, backend=None):
        """Return a user-friendly string representation of track."""
        if backend is None:
            backend = self.backend
        return app.frame.track_format_template.render(
            **asdict(track), backend=backend
        )

    def add_result(self, track, backend=None):
        """Adds a Track instance to self.results."""
        if backend is None:
            backend = self.backend
        res = self.results.Append(self.stringify(track, backend=backend))
        track.index = res
        self.results.SetClientData(res, track)
        if not res:
            if isinstance(self.FindFocus(), wx.TextCtrl):
                self.results.SetFocus()
            self.results.SetSelection(0)
        return res

    def add_results(self, results, clear=True, backend=None):
        """Add multiple results to self.results."""
        if clear:
            self.results.Clear()

        def f():
            """Add a result."""
            if not results:
                return True
            result = results.pop(0)
            wx.CallAfter(self.add_result, result, backend=backend)

        add_job('Add Results', f)

    def get_result(self):
        """Get and return the currently-selected result."""
        i = self.results.GetSelection()
        if i >= 0:
            return self.results.GetClientData(i)

    def on_activate(self, event):
        """An entry in self.results has been clicked."""
        res = self.get_result()
        if res is not None:
            logger.info('Activated %r.', res)
            sound.play(res)
            sound.queue.clear()
            for index in range(res.index + 1, self.results.Count):
                sound.queue.append(self.results.GetClientData(index))
                logger.info('Queued %r.', sound.queue[-1])
        else:
            wx.Bell()
