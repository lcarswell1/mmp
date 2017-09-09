"""Provides the GlobalBackendPanel class."""

import logging
from functools import partial
from .backend_panel import BackendPanel
from ...jobs import add_job
from ... import app

logger = logging.getLogger(__name__)


class GlobalBackendPanel(BackendPanel):
    def __init__(self, *args, **kwargs):
        super(GlobalBackendPanel, self).__init__(None, *args, **kwargs)
        self.search_label.SetLabel('&Global Search')

    def on_search(self, event):
        """Search all backends."""
        text = self.search_field.GetValue()
        logger.debug('Search: %s.', text)
        for backend in app.frame.backends:
            add_job(
                'Add results from %s' % backend.name,
                partial(self.do_search, text, backend=backend), one_shot=True
            )
