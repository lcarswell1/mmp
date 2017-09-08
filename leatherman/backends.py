"""Provides the Backend class, as well as the make_backend function."""

import logging
from threading import Thread
import wx
from attr import attrs, attrib, Factory
from . import app

logger = logging.getLogger(__name__)


class BackendError(Exception):
    pass


@attrs
class Backend:
    """A backend for playing music."""

    name = attrib()
    description = attrib()
    loop_func = attrib()
    node = attrib(default=Factory(lambda: None), init=False)

    def __attrs_post_init__(self):
        """Start loop_func if it's not None."""
        if self.loop_func is not None:
            self.thread = Thread(target=self.loop)
            self.thread.start()

    def loop(self):
        """Start this backend's loop."""
        while app.running:
            try:
                self.loop_func(self)
            except Exception as e:
                logger.error('Error in loop: %r.', self)
                logger.exception(e)
                wx.CallAfter(app.frame.on_error, e)
                break

    @classmethod
    def from_module(cls, module):
        """Return a Backend instance made from a module."""
        if hasattr(module, 'name'):
            return cls(
                module.name, getattr(module, 'description', ''),
                getattr(module, 'loop_func', None)
            )
        else:
            raise BackendError(
                'The backend loaded from %r has no name.' % module
            )
