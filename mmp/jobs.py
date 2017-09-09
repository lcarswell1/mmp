"""The jobs framework."""

import logging
from time import time
import wx
from attr import attrs, attrib, Factory
from . import app

logger = logging.getLogger(__name__)
jobs = []


@attrs
class Job:
    """A job object."""

    name = attrib()
    func = attrib()
    run_every = attrib()
    last_run = attrib(default=Factory(int), init=False)


def run_jobs():
    while app.running:
        if not jobs:
            continue  # Nothing to do.
        now = time()
        job = jobs.pop(0)
        if job.run_every is None or (
            now - job.last_run >= job.run_every
        ):
            try:
                dont_stop = job.func()
                job.last_run = time()
                if not dont_stop:
                    jobs.append(job)
            except Exception as e:
                logger.exception(e)
                wx.CallAfter(
                    app.frame.on_error,
                    'Error with job %s: %s.' % (job.name, e)
                )


def add_job(name, func, run_every=None):
    """Add a job to the jobs queue. If func returns True the job will never run
    again. If run_every is not None run the job when the given time has
    elapsed."""
    j = Job(name, func, run_every)
    jobs.append(j)
    return j
