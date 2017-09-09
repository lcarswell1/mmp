"""Provides the GlobalBackendPanel class."""

from .backend_panel import BackendPanel
from ... import app


class GlobalBackendPanel(BackendPanel):
    def __init__(self, *args, **kwargs):
        super(GlobalBackendPanel, self).__init__(None, *args, **kwargs)
        self.search_label.SetLabel('&Global Search')

    def on_search(self, event):
        app.frame.on_error('Global search.')
