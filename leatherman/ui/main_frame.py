"""Provides the MainFrame class."""

import wx
from .panels import LeftPanel, RightPanel


class MainFrame(wx.Frame):
    """The main frame for the player."""

    def __init__(self, *args, **kwargs):
        """Initialise the frame."""
        super(MainFrame, self).__init__(*args, **kwargs)
        self.splitter = wx.SplitterWindow(self)
        self.left_panel = LeftPanel(self.splitter)
        self.right_panel = RightPanel(self.splitter)
        self.splitter.SplitHorizontally(self.left_panel, self.right_panel)
