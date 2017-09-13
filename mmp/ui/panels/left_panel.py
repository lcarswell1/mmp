"""Provides the Leftpanel class."""

import logging
import wx
from simpleconf import Section
from simpleconf.dialogs.wx import SimpleConfWxPanel
from .hotkey_panel import HotkeyPanel
from .right_panel import RightPanel
from .global_backend_panel import GlobalBackendPanel
from ...backends import Backend
from ...config import config
from ... import sound, app
from ...db import DBProxy, Hotkey

logger = logging.getLogger(__name__)


class LeftPanel(wx.Panel):
    """The left panel of the mainframe."""

    def __init__(self, *args, **kwargs):
        """Add controls."""
        super(LeftPanel, self).__init__(*args, **kwargs)
        self.global_backend_panel = None
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
        ss = wx.GridSizer(2, 0, 0)  # Status sizer.
        ss.Add(wx.StaticText(self, label='Track &Position'), 0, wx.GROW)
        self.position = wx.Slider(self, style=wx.SL_HORIZONTAL)
        self.position.Bind(
            wx.EVT_SLIDER,
            lambda event: self.set_position(event.EventObject.GetValue())
        )
        ss.Add(self.position, 1, wx.GROW)
        ss.Add(wx.StaticText(self, label='&Volume'), 0, wx.GROW)
        self.volume = wx.Slider(self, style=wx.SL_LEFT)
        self.volume.Bind(
            wx.EVT_SLIDER,
            lambda event: app.frame.set_volume(event.EventObject.GetValue())
        )
        ss.Add(self.volume, 1, wx.GROW)
        s.Add(ss, 0, wx.GROW)
        self.SetSizerAndFit(s)

    def on_previous(self, event):
        """Play the previous track."""
        if isinstance(self.FindFocus(), wx.TextCtrl):
            return event.Skip()
        if sound.played:
            track = sound.played.pop()
        else:
            return wx.Bell()
        if sound.new_stream is not None:
            sound.queue.insert(0, sound.new_stream.track)
        sound.play(track, mark_played=False)

    def on_play_pause(self, event):
        """Play or pause the current track."""
        if isinstance(self.FindFocus(), (wx.TextCtrl, wx.Button)):
            return event.Skip()
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
        if isinstance(self.FindFocus(), wx.TextCtrl):
            return event.Skip()
        if sound.queue:
            track = sound.queue.pop(0)
        else:
            return wx.Bell()
        sound.play(track)

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
        elif isinstance(data, Section):  # Configuration.
            new = SimpleConfWxPanel(data, splitter)
        elif isinstance(data, Backend):  # One of the backends.
            config.interface['last_backend'] = data.short_name
            new = data.panel
        elif item == app.frame.backends_root:
            config.interface['last_backend'] = ''
            if self.global_backend_panel is None:
                self.global_backend_panel = GlobalBackendPanel(splitter)
                logger.debug('Created %r.', self.global_backend_panel)
            new = self.global_backend_panel
        elif isinstance(data, DBProxy) and data.cls is Hotkey:
            if data.panel is None:
                data.panel = HotkeyPanel(data, splitter)
            new = data.panel
        else:
            new = wx.Panel(splitter)
        logger.debug('Replacing frame %r with %r.', old, new)
        splitter.ReplaceWindow(old, new)
        new.Show(True)
        if isinstance(old, SimpleConfWxPanel):
            old.on_ok(event)
            old.Destroy()
        else:
            logger.debug('Hiding panel %r.', old)
            old.Hide()

    def set_position(self, value, relative=False):
        """Seek to value. If relative evaluates to True values such as -5 or 10
        are allowed. Otherwise a percentage is expected."""
        if sound.new_stream is None:
            return self.position.SetValue(0)
        elif isinstance(self.FindFocus(), wx.TextCtrl):
            return wx.Bell()
        stream = sound.new_stream.stream
        length = stream.get_length() - 1
        if relative:
            # Create a percentage:
            value = max(0, min(100, (100 / length * stream.position) + value))
        actual_value = min(length, int(length / 100 * value))
        logger.info('Setting position: %d%% (%d).', value, actual_value)
        stream.position = actual_value
        self.position.SetValue(value)

    def rewind(self, event):
        """Rewind a little bit."""
        self.set_position(-1, relative=True)

    def fastforward(self, event):
        """Fast forward a little bit."""
        self.set_position(1, relative=True)
