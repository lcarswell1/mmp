"""
Youtube backend.

Some code was inspired by the accepted answer from this link:
https://stackoverflow.com/questions/29069444/returning-the-urls-from-a-youtube-search

Massive thanks to the poster!
"""

import logging
import os.path
from urllib.parse import quote
import wx
from pyperclip import copy
from pytube import YouTube
from sound_lib.stream import FileStream
from attr import attrs, attrib, Factory
from requests import get
from bs4 import BeautifulSoup
from mmp.tracks import Track

logger = logging.getLogger(__name__)
extension = 'mp4'

name = 'Youtube'
description = 'An audio-only Youtube interface.'
backend = None

base_url = 'https://youtube.com/results?search_query={}'
video_url = 'https://www.youtube.com{}'


@attrs
class YoutubeTrack(Track):
    """Add a URL attribute."""

    url = attrib(default=Factory(lambda: None))

    def get_stream(self):
        """Return a filestream representing this object."""
        y = YouTube(self.url)
        path = os.path.join(
            backend.get_download_path(), '%s.%s' % (y.filename, extension)
        )
        if not os.path.isfile(path):
            v = y.filter(extension=extension)[-1]
            v.download(backend.get_download_path())
            backend.register_file(path)
        return FileStream(
            file=path
        )


def copy_url(event):
    """Copy the URL of the current track."""
    res = backend.panel.get_result()
    if res is None:
        return wx.Bell()
    copy(res.url)


def on_init(backend):
    """Add a copy item to the menu."""
    backend.panel.Bind(
        wx.EVT_MENU, copy_url,
        backend.panel.menu.Append(
            wx.ID_ANY, '&Copy URL', 'Copy the URL of the current video.'
        )
    )


def on_search(value):
    r = get(base_url.format(quote(value)))
    if not r.ok:
        raise ValueError('Error %d.' % r.status_code)  # Something went wrong.
    logger.info('URL: %s.', r.url)
    s = BeautifulSoup(r.content, 'html.parser')
    results = s.find_all(attrs={'class': 'yt-uix-tile-link'})
    logger.info('Results: %d.', len(results))
    videos = []
    for vid in results:
        artist = vid.parent.parent.find(attrs={'class': 'g-hovercard'})
        if artist is None:
            artist = 'Unknown Artist'
        else:
            artist = artist.text
        video = YoutubeTrack(
            artist,
            None, None, vid.text,
            url=video_url.format(vid['href'])
        )
        videos.append(video)
    return videos
