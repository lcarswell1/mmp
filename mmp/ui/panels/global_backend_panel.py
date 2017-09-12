"""Provides the GlobalBackendPanel class."""

import logging
from functools import partial
import wx
from .backend_panel import BackendPanel
from ...jobs import add_job
from ... import app

logger = logging.getLogger(__name__)


class GlobalBackendPanel(BackendPanel):
    def __init__(self, *args, **kwargs):
        super(GlobalBackendPanel, self).__init__(None, *args, **kwargs)
        self.search_label.SetLabel('&Global Search')

    def do_search(self, text, backend=None):
        """This method will be called as a job to gather the results from
        the on_search hook of the provided backend (or self.backend) and pass
        them to self.add_results."""
        if backend is None:
            backend = self.backend
        logger.debug('Searching %r for %s.', backend, text)
        results = backend.on_search(text)
        if results:
            wx.CallAfter(
                self.add_results, results, clear=False, backend=backend
            )
        return True

    def on_search(self, event):
        """Search all backends."""
        self.results.Clear()
        text = self.search_field.GetValue()
        self.search_field.Clear()
        logger.debug('Search: %s.', text)
        for backend in app.frame.backends:
            add_job(
                'Add results from %s' % backend.name,
                partial(self.do_search, text, backend=backend)
            )
