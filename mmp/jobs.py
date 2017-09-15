"""The jobs framework."""

import logging
from time import time
import wx
from attr import attrs, attrib, Factory
from . import app

logger = logging.getLogger(__name__)
current_job = None
jobs = []


@attrs
class Job:
    """A job object."""

    name = attrib()
    func = attrib()
    run_every = attrib()
    last_run = attrib(default=Factory(int), init=False)


def run_jobs():
    global current_job
    while app.running:
        if not jobs:
            continue  # Nothing to do.
        now = time()
        current_job = jobs.pop(0)
        if current_job.run_every is None or (
            now - current_job.last_run >= current_job.run_every
        ):
            try:
                dont_stop = current_job.func()
                current_job.last_run = time()
                if dont_stop:
                    current_job = None
                    continue
            except Exception as e:
                logger.exception(e)
                wx.CallAfter(
                    app.frame.on_error,
                    'Error with current_job %s: %s.' % (current_job.name, e)
                )
                current_job = None
                continue
        jobs.append(current_job)
        current_job = None


def all_jobs():
    """Get a list of all the running jobs including the current one."""
    l = jobs.copy()
    if current_job is not None:
        l.append(current_job)
    return l


def add_job(name, func, run_every=None):
    """Add a job to the jobs queue. If func returns True the job will never run
    again. If run_every is not None run the job when the given time has
    elapsed."""
    j = Job(name, func, run_every)
    jobs.append(j)
    return j
