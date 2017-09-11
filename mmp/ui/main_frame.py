"""Provides the MainFrame class."""

import logging
from threading import Thread
from inspect import isclass
import wx
import six
from attr import attrs, attrib
import backends
from .. import app
from ..jobs import run_jobs
from ..backends import Backend
from .panels.left_panel import LeftPanel
from .panels.right_panel import RightPanel
from ..app import name
from ..config import config
from ..hotkeys import handle_hotkey, add_hotkey, functions, section_media
from ..db import session, Section, Hotkey

logger = logging.getLogger(__name__)


@attrs
class DBProxy:
    """Represents an entry in one of the database tables."""

    cls = attrib()
    id = attrib()


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
            wx.WXK_LEFT, self.left_panel.on_previous, modifiers=wx.ACCEL_CTRL,
            section_id=section_media
        )
        add_hotkey(
            wx.WXK_SPACE, self.left_panel.on_play_pause,
            section_id=section_media
        )
        add_hotkey(
            wx.WXK_RIGHT, self.left_panel.on_next, modifiers=wx.ACCEL_CTRL,
            section_id=section_media
        )
        add_hotkey(wx.WXK_RETURN, self.on_activate)
        add_hotkey(wx.WXK_MENU, self.on_context)
        add_hotkey(
            wx.WXK_F10, self.on_context, modifiers=wx.ACCEL_SHIFT)
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

    def add_section(self, section, root=None):
        """Add a section recursively with all its options to the provided
        section or self.hotkeys_root."""
        if root is None:
            root = self.hotkeys_root
        section_item = self.tree.AppendItem(root, section.name)
        self.tree.SetItemData(section_item, DBProxy(Section, section.id))
        if section.children or section.hotkeys:
            self.tree.SetItemHasChildren(section_item)
        logger.info('Added %r.', section)
        for subsection in section.children:
            self.add_section(subsection, section_item)
        for hotkey in section.hotkeys:
            hotkey_item = self.tree.AppendItem(
                section_item, functions[
                    (hotkey.control_id, hotkey.func_name)
                ].__doc__
            )
            self.tree.SetItemData(hotkey_item, DBProxy(Hotkey, hotkey.id))
            logger.info('Added %r.', hotkey)

    def on_activate(self, event):
        """Handle the return key probably."""
        c = event.EventObject
        p = c.GetParent()
        if isinstance(c, wx.TextCtrl):
            func = p.on_search
        elif isinstance(c, wx.ListBox):
            func = p.on_activate
        else:
            return event.Skip()
        func(event)

    def on_context(self, event):
        """Handle the applications key ETC."""
        c = event.EventObject
        p = c.GetParent()
        if isinstance(c, wx.ListBox):
            p.on_context(event)

    def on_show(self, event):
        """Populate the tree."""
        event.Skip()
        self.root = self.tree.AddRoot(name)
        self.backends_root = self.tree.AppendItem(self.root, 'Backends')
        self.hotkeys_root = self.tree.AppendItem(self.root, 'Hotkeys')
        for root in (self.root, self.backends_root, self.hotkeys_root):
            self.tree.SetItemHasChildren(root)
        self.config_root = self.add_config(self.root, config)
        self.load_backends()
        self.tree.ExpandAll()
        self.tree.Collapse(self.config_root)
        config.load()
        with session() as s:
            # Clear out inactive hotkeys.
            s.query(Hotkey).filter_by(active=False).delete()
            for section in s.query(Section).filter_by(parent=None):
                self.add_section(section)
        if config.interface['last_backend']:
            for b in self.backends:
                if b.short_name == config.interface['last_backend']:
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
        if isclass(message):
            message = message.__name__
        elif not isinstance(message, six.string_types):
            message = str(message)
        return wx.MessageBox(message, title, style=style)

    def backend_from_module(self, module):
        """Load a module and add it to self.backends."""
        logger.info('Making a backend from %r.', module)
        try:
            backend = Backend.from_module(self, module)
            backend.module = module
            logger.info('Created %r.', backend)
        except Exception as e:
            logger.exception(e)
            return self.on_error(e)
        self.add_backend(backend)

    def add_backend(self, backend):
        """Add a backend object."""
        self.backends.append(backend)
        logger.info('Added %r.', backend)
        self.tree.SetItemHasChildren(backend.root)
        backend.node = self.tree.AppendItem(backend.root, backend.name)
        self.tree.SetItemData(backend.node, backend)
        if hasattr(backend.module, 'on_init'):
            try:
                backend.module.on_init(backend)
            except Exception as e:
                self.on_error(
                    f'Error initialising {backend.name}: {e}.'
                )
                logger.exception(e)

    def load_backends(self):
        """Load the back ends."""
        self.backends.clear()
        self.tree.DeleteChildren(self.backends_root)
        for module in backends.backends:
            self.backend_from_module(module)
        logger.info('Backends loaded: %d.', len(self.backends))
