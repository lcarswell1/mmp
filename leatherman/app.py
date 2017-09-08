"""The wx app."""

import wx

app = wx.App(False)

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
