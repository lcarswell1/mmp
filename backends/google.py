"""A Google Play Music backend."""

import wx
from gmusicapi import Mobileclient
from simpleconf import Section, Option

name = "Google Play Music"
api = Mobileclient()
backend = None
authenticated = False


def try_login():
    global authenticated
    if authenticated:
        return  # Already logged in.
    authenticated = api.login(
        config.login['username'], config.login['password'],
        api.FROM_MAC_ADDRESS
    )
    if not authenticated:
        raise RuntimeError(
            'Login failed. Check your username and password and try again.'
        )


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


def on_search(value):
    """Search for the provided value."""
    if not value:
        return False
    try_login()
    results = api.search(value)
    backend.frame.on_error(results.keys())
    return True
