"""Provides the Leftpanel class."""

import logging
import wx
from simpleconf import Section
from simpleconf.dialogs.wx import SimpleConfWxPanel
from .right_panel import RightPanel
from .backend_panel import BackendPanel
from ...backends import Backend
from ...config import config
from ... import sound

logger = logging.getLogger(__name__)


class LeftPanel(wx.Panel):
    """The left panel of the mainframe."""

    def __init__(self, *args, **kwargs):
        """Add controls."""
        super(LeftPanel, self).__init__(*args, **kwargs)
        s = wx.BoxSizer(wx.VERTICAL)  # Main sizer.
        self.tree = wx.TreeCtrl(self)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_change)
        s.Add(self.tree, 1, wx.GROW)
        bs = wx.BoxSizer(wx.HORIZONTAL)  # Button sizer.
        self.previous_button = wx.Button(self, label='&Previous')
        self.previous_button.Bind(wx.EVT_BUTTON, self.on_previous)
        self.play_pause_button = wx.Button(self, label='&Play')
        self.play_pause_button.Bind(wx.EVT_BUTTON, self.on_play_pause)
        self.next_button = wx.Button(self, label='&Next')
        self.next_button.Bind(wx.EVT_BUTTON, self.on_next)
        bs.AddMany(
            (
                (self.previous_button, 0, wx.GROW),
                (self.play_pause_button, 1, wx.GROW),
                (self.next_button, 0, wx.GROW)
            )
        )
        s.Add(bs, 0, wx.GROW)
        ss = wx.BoxSizer(wx.HORIZONTAL)  # Status sizer.
        ss.Add(wx.StaticText(self, label='&Status'), 0, wx.GROW)
        self.status = wx.TextCtrl(self, style=wx.TE_READONLY)
        ss.Add(self.status, 1, wx.GROW)
        s.Add(ss, 0, wx.GROW)
        self.SetSizerAndFit(s)

    def on_previous(self, event):
        """Play the previous track."""
        wx.Bell()

    def on_play_pause(self, event):
        """Play or pause the current track."""
        if sound.new_stream is None:
            wx.Bell()
        else:
            stream = sound.new_stream.stream
            if stream.is_paused:
                stream.play()
            else:
                stream.pause()

    def on_next(self, event):
        """Play the next track."""
        wx.Bell()

    def on_tree_change(self, event):
        """The tree view has changed selection."""
        item = event.GetItem()
        data = self.tree.GetItemData(item)
        splitter = self.GetParent()
        old = splitter.GetWindow2()
        if item == self.tree.RootItem:  # Root node.
            if not isinstance(old, RightPanel):
                new = splitter.GetParent().right_panel
            else:
                return  # Nothing more to do.
        elif isinstance(data, Section):
            new = SimpleConfWxPanel(data, splitter)
        elif isinstance(data, Backend):
            config.interface['last_backend'] = data.name
            new = data.panel
        else:
            new = wx.Panel(splitter)
        logger.info('Replacing frame %r with %r.', old, new)
        splitter.ReplaceWindow(old, new)
        new.Show(True)
        if isinstance(old, (RightPanel, BackendPanel)):
            old.Hide()
        else:
            if isinstance(old, SimpleConfWxPanel):
                old.on_ok(event)
            old.Destroy()
