"""The main menu for the application."""

import wx
from .view_menu import ViewMenu


class MenuBar(wx.MenuBar):
    """The main menu."""

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super(MenuBar, self).__init__(*args, **kwargs)
        for cls in [ViewMenu]:
            self.Append(cls(parent), cls.name)
