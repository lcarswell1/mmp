"""The wx app."""

import wx
from jinja2 import Environment

running = True  # Set to False when we close.
app = wx.App(False)

frame = None  # The main frame.

name = 'Leatherman'
version = '0.1Pre'
description = 'The multitool of media players.'

authors = (
    'Chris Norman',
)

app.SetAppName(name)

paths = wx.StandardPaths.Get()

data_dir = paths.GetUserDataDir()
media_dir = paths.GetUserLocalDataDir()
backends_dir = 'backends'
environment = Environment()
