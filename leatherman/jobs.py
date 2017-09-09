"""The jobs framework."""

import logging
import wx
from attr import attrs, attrib
from . import app

logger = logging.getLogger(__name__)
jobs = []


@attrs
class Job:
    """A job object."""

    name = attrib()
    func = attrib()


def run_jobs():
    while app.running:
        if not jobs:
            continue  # Nothing to do.
        job = jobs.pop(0)
        try:
            job.func()
            jobs.append(job)
        except Exception as e:
            logger.exception(e)
            wx.CallAfter(
                app.frame.on_error, 'Error with job %s: %s.' % (job.name, e)
            )


def add_job(name, func):
    """Add a job to the jobs queue."""
    j = Job(name, func)
    jobs.append(j)
    return j
