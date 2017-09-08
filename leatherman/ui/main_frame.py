"""Provides the MainFrame class."""

import logging
import wx
from import_directory import import_directory
from .. import app
from ..backends import Backend
from .panels import LeftPanel, RightPanel
from ..app import name

logger = logging.getLogger(__name__)


class MainFrame(wx.Frame):
    """The main frame for the player."""

    def __init__(self, *args, **kwargs):
        """Initialise the frame."""
        super(MainFrame, self).__init__(*args, **kwargs)
        s = wx.BoxSizer(wx.VERTICAL)
        self.splitter = wx.SplitterWindow(self)
        self.left_panel = LeftPanel(self.splitter)
        self.tree = self.left_panel.tree  # Shorthand.
        self.right_panel = RightPanel(self.splitter)
        self.splitter.SplitHorizontally(self.left_panel, self.right_panel)
        s.Add(self.splitter, 1, wx.GROW)
        self.SetSizerAndFit(s)
        self.Bind(wx.EVT_SHOW, self.on_show)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.backends = []  # To be populated by self.reload_backends.

    def on_show(self, event):
        """Populate the tree."""
        event.Skip()
        self.root = self.tree.AddRoot(name)
        self.tree.SetItemHasChildren(self.root)
        self.backends_root = self.tree.AppendItem(self.root, 'Backends')
        self.tree.SetItemHasChildren(self.backends_root)
        self.reload_backends()
        self.tree.ExpandAll()

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

    def load_backend(self, module, reloaded):
        """Load (or reload) a module and add it to self.backends."""
        if reloaded:
            action = 'Reloaded'
        else:
            action = 'Loaded'
        logger.info('%s %r.', action, module)
        try:
            backend = Backend.from_module(module)
            self.backends.append(backend)
        except Exception as e:
            return self.on_error(e)
        backend.node = self.tree.AppendItem(self.backends_root, backend.name)

    def reload_backends(self):
        """Reload the back ends."""
        self.backends.clear()
        self.tree.DeleteChildren(self.backends_root)
        import_directory(app.backends_dir, func=self.load_backend)
