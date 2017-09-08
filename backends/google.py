"""A Google Play Music backend."""

import wx
from simpleconf import Section, Option

name = "Google Play Music"


class Config(Section):
    """Configuration for this backend."""

    class login(Section):
        """Login credentials."""
        title = 'Login'

        username = Option('', title='&Username')
        password = Option(
            '', title='&Password',
            control=lambda option, window: wx.TextCtrl(
                window, style=wx.TE_PASSWORD
            )
        )
        option_order = (username, password)


config = Config()
