"""Provides the Backend class, as well as the make_backend function."""

import logging
from threading import Thread
import wx
from attr import attrs, attrib, Factory
from simpleconf import Section
from . import app
from .ui.panels.backend_panel import BackendPanel
from .config import config

logger = logging.getLogger(__name__)


class BackendError(Exception):
    pass


@attrs
class Backend:
    """A backend for playing music."""

    frame = attrib()
    short_name = attrib()
    name = attrib()
    description = attrib()
    loop_func = attrib()
    config = attrib()
    on_search = attrib()
    panel = attrib()
    node = attrib(default=Factory(lambda: None), init=False)

    def __attrs_post_init__(self):
        """Start loop_func if it's not None."""
        if self.config is not None:
            if self.config.title == Section.title:
                self.config.title = self.name
            config.backends.add_section(self.short_name, self.config)
            self.frame.add_config(self.frame.backends_config_root, self.config)
        self.panel = self.panel(self, self.frame.splitter)
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
    def from_module(cls, frame, module):
        """Return a Backend instance made from a module. The Backend instance
        will have a frame attribute which is the main frame of the
        application."""
        if hasattr(module, 'name'):
            b = cls(
                frame, module.__name__, module.name, getattr(
                    module, 'description', ''
                ),
                getattr(module, 'loop_func', None),
                getattr(module, 'config', None),
                getattr(module, 'on_search', frame.on_error),
                getattr(module, 'BackendPanel', BackendPanel)
            )
            module.backend = b
            if hasattr(module, 'on_init'):
                module.on_init(b)
            return b
        else:
            raise BackendError(
                'The backend loaded from %r has no name.' % module
            )
