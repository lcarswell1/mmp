"""Provides the BackendPanel class."""

import logging
import wx
from wx.lib.sized_controls import SizedPanel
from attr import asdict
from ... import app, sound
from ...hotkeys import Hotkey

logger = logging.getLogger(__name__)


class BackendPanel(SizedPanel):
    """The default panel used by Backend instances."""

    def __init__(self, backend, *args, **kwargs):
        """Initialise an add some controls."""
        self.backend = backend
        self.hotkeys = []
        super(BackendPanel, self).__init__(*args, **kwargs)
        self.SetSizerType('form')
        self.search_label = wx.StaticText(self, label='&Search')
        self.search_field = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.search_field.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        self.results_label = wx.StaticText(self, label='&Results')
        self.results = wx.ListBox(self)
        self.add_hotkey(
            0, wx.WXK_RETURN, self.on_activate, control=self.results
        )
        self.rebuild_accelerator_table()

    def rebuild_accelerator_table(self):
        """Rebuild the accelerator table from self.hotkeys."""
        d = {}
        for hotkey in self.hotkeys:
            entry = (hotkey.modifiers, hotkey.key, hotkey.id)
            l = d.get(hotkey.control, [])
            l.append(entry)
            d[hotkey.control] = l
        for control, tbl in d.items():
            control.SetAcceleratorTable(wx.AcceleratorTable(tbl))

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

    def add_hotkey(self, modifiers, key, func, id=None, control=None):
        """Add a hotkey. You can either specify key as an integer or a string
        which will be passed through ord. If control is None it will default to
        this panel. Otherwise you can bind the hotkey to any control you
        like."""
        if id is None:
            id = wx.NewId()
        if control is None:
            control = self
        control.Bind(wx.EVT_MENU, func, id=id)
        h = Hotkey(modifiers, key, func, id, control)
        self.hotkeys.append(h)
        self.rebuild_accelerator_table()

    def get_result(self):
        """Get and return the currently-selected result."""
        i = self.results.GetSelection()
        if i >= 0:
            return self.results.GetClientData(i)

    def on_activate(self, event):
        """An entry in self.results has been clicked."""
        if not self.results.HasFocus():
            return event.Skip()
        res = self.get_result()
        if res is not None:
            logger.info('Playing %r.', res)
            sound.play(res.get_stream())
        else:
            wx.Bell()
