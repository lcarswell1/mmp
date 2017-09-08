"""Provides the BackendPanel class."""

import wx
from wx.lib.sized_controls import SizedPanel


class BackendPanel(SizedPanel):
    """The default panel used by Backend instances."""

    def __init__(self, backend, *args, **kwargs):
        """Initialise an add some controls."""
        self.backend = backend
        super(BackendPanel, self).__init__(*args, **kwargs)
        self.SetSizerType('form')
        self.search_label = wx.StaticText(self, label='&Search')
        self.search_field = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.search_field.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        self.results_label = wx.StaticText(self, label='&Results')
        self.results = wx.ListBox(self)

    def on_search(self, event):
        """The enter key was pressed in the search field."""
        text = self.search_field.GetValue()
        self.search_field.Clear()
        try:
            self.backend.on_search(text)
        except Exception as e:
            self.backend.frame.on_error(e)
