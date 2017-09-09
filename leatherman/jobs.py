"""The jobs framework."""

import logging
import wx
from . import app

logger = logging.getLogger(__name__)
jobs = []


def run_jobs():
    while app.running:
        if not jobs:
            continue  # Nothing to do.
        f = jobs.pop(0)
        try:
            f()
            jobs.append(f)
        except Exception as e:
            wx.CallAfter(app.frame.on_error, 'Error with job %r: %s.' % (f, e))
            logger.exception(e)
