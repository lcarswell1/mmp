"""Provides the Leftpanel class."""

import wx
from .right_panel import RightPanel


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
        self.play_pause_button = wx.Button(self, label='&Play')
        self.next_button = wx.Button(self, label='&Next')
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

    def on_tree_change(self, event):
        """The tree view has changed selection."""
        item = event.GetItem()
        data = self.tree.GetItemData(item)
        splitter = self.GetParent()
        old = splitter.GetWindow2()
        if data is None:  # Root node.
            if not isinstance(old, RightPanel):
                splitter.ReplaceWindow(old, RightPanel(splitter))
            splitter.GetWindow2().on_show(event)
        else:
            wx.MessageBox(repr(data))
