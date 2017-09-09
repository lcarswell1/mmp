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
    one_shot = attrib()


def run_jobs():
    while app.running:
        if not jobs:
            continue  # Nothing to do.
        job = jobs.pop(0)
        try:
            job.func()
            if not job.one_shot:
                jobs.append(job)
        except Exception as e:
            logger.exception(e)
            wx.CallAfter(
                app.frame.on_error, 'Error with job %s: %s.' % (job.name, e)
            )


def add_job(name, func, one_shot=False):
    """Add a job to the jobs queue. If one_shot is True the job will only be
    run once."""
    j = Job(name, func, one_shot)
    jobs.append(j)
    return j
