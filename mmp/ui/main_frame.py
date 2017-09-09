"""Provides the MainFrame class."""

import logging
from threading import Thread
import wx
import backends
from .. import app
from ..jobs import run_jobs
from ..backends import Backend
from .panels.left_panel import LeftPanel
from .panels.right_panel import RightPanel
from ..app import name
from ..config import config
from ..hotkeys import handle_hotkey, add_hotkey

logger = logging.getLogger(__name__)


class MainFrame(wx.Frame):
    """The main frame for the player."""

    def __init__(self, *args, **kwargs):
        """Initialise the frame."""
        super(MainFrame, self).__init__(*args, **kwargs)
        self.track_format_template = None  # Set by config.
        s = wx.BoxSizer(wx.VERTICAL)
        self.splitter = wx.SplitterWindow(self)
        self.left_panel = LeftPanel(self.splitter)
        self.Bind(wx.EVT_CHAR_HOOK, handle_hotkey)
        add_hotkey(
            wx.WXK_LEFT, self.left_panel.on_previous, modifiers=wx.ACCEL_CTRL
        )
        add_hotkey(wx.WXK_SPACE, self.left_panel.on_play_pause)
        add_hotkey(
            wx.WXK_RIGHT, self.left_panel.on_next, modifiers=wx.ACCEL_CTRL
        )
        self.tree = self.left_panel.tree  # Shorthand.
        self.right_panel = RightPanel(self.splitter)
        self.splitter.SplitHorizontally(self.left_panel, self.right_panel)
        s.Add(self.splitter, 1, wx.GROW)
        self.SetSizerAndFit(s)
        self.Bind(wx.EVT_SHOW, self.on_show)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.backends = []  # To be populated by self.load_backends.
        self.jobs_thread = Thread(target=run_jobs)
        self.jobs_thread.start()

    def on_show(self, event):
        """Populate the tree."""
        event.Skip()
        self.root = self.tree.AddRoot(name)
        self.tree.SetItemHasChildren(self.root)
        self.backends_root = self.tree.AppendItem(self.root, 'Backends')
        self.tree.SetItemHasChildren(self.backends_root)
        self.config_root = self.add_config(self.root, config)
        self.load_backends()
        self.tree.ExpandAll()
        self.tree.Collapse(self.config_root)
        config.load()
        if config.interface['last_backend']:
            for b in self.backends:
                if b.name == config.interface['last_backend']:
                    self.tree.SelectItem(b.node)
                    return logger.info('Setting focus to %r.', b)
            else:
                logger.info(
                    'Could not find backend %s.',
                    config.interface['last_backend']
                )
        else:
            logger.info(
                'No last backend set: %r.', config.interface['last_backend']
            )
        self.tree.SelectItem(self.backends_root)

    def add_config(self, root, section):
        """Add an entry to self.tree for section under root."""
        item = self.tree.AppendItem(root, section.title)
        if section is config.backends:
            self.backends_config_root = item
        self.tree.SetItemData(item, section)
        if section.sections or section is config.backends:
            self.tree.SetItemHasChildren(item)
            for subsection in section.children:
                self.add_config(item, subsection)
        return item

    def on_close(self, event):
        """Set app.running to false before we close."""
        app.running = False
        event.Skip()

    def on_error(self, message, title=None, style=None):
        """Display an error."""
        if title is None:
            title = 'Error'
        if style is None:
            style = wx.ICON_EXCLAMATION
        return wx.MessageBox(str(message), title, style=style)

    def add_backend(self, module):
        """Load a module and add it to self.backends."""
        logger.info('Making a backend from %r.', module)
        try:
            backend = Backend.from_module(self, module)
            logger.info('Created %r.', backend)
            self.backends.append(backend)
        except Exception as e:
            logger.exception(e)
            return self.on_error(e)
        backend.node = self.tree.AppendItem(self.backends_root, backend.name)
        self.tree.SetItemData(backend.node, backend)
        if hasattr(module, 'on_init'):
            module.on_init(backend)

    def load_backends(self):
        """Load the back ends."""
        self.backends.clear()
        self.tree.DeleteChildren(self.backends_root)
        for backend in backends.backends:
            self.add_backend(backend)
        logger.info('Backends loaded: %d.', len(self.backends))
