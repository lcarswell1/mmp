"""
Youtube backend.

Some code was inspired by the accepted answer from this link:
https://stackoverflow.com/questions/29069444/returning-the-urls-from-a-youtube-search

Massive thanks to the poster!
"""

import logging
import webbrowser
from urllib.parse import quote, urljoin
import wx
from pyperclip import copy
from pytube import YouTube
from sound_lib.stream import FileStream, URLStream
from attr import attrs, attrib, Factory
from requests import get
from bs4 import BeautifulSoup
from mmp.tracks import Track
from mmp.jobs import add_job
from mmp.backends import DownloadStates

logger = logging.getLogger(__name__)
extension = 'mp4'

name = 'Youtube'
description = 'An audio-only Youtube interface.'
backend = None

base_url = 'https://youtube.com/results?search_query={}'
video_url = 'https://www.youtube.com'


class YoutubeError(Exception):
    pass


@attrs
class YoutubeTrack(Track):
    """Add a URL attribute."""

    url = attrib(default=Factory(lambda: None))

    def get_stream(self):
        """Return a filestream representing this object."""
        try:
            y = YouTube(self.url)
        except Exception as e:
            logger.critical('Failed to get a Youtube object from %r.', self)
            if isinstance(e, AttributeError):
                webbrowser.open(self.url)
                raise YoutubeError(
                    'Unable to play. Opening in your default web browser.'
                )
            raise e
        v = y.filter(extension=extension)[-1]
        name = '%s.%s' % (v.filename, extension)
        state = backend.get_download_state(name)
        if state is DownloadStates.downloaded:
            return FileStream(file=backend.get_full_path(name))
        else:
            if state is DownloadStates.none:
                add_job(
                    'Download track %r' % self,
                    lambda: backend.download_file(v.url, name)
                )
            return URLStream(v.url.encode())


class YoutubeChannel(YoutubeTrack):
    """A youtube user."""

    def __init__(self, name, url):
        super(YoutubeChannel, self).__init__(
            'Youtube Channel', None, None, name,
            url=urljoin(video_url, url, 'videos')
        )

    def activate(self):
        """Show channel videos."""
        backend.panel.add_results(
            get_results_from_url(self.url, artist=self.title)
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
    """Get a list of YoutubeTrack instances."""
    return get_results_from_url(base_url.format(quote(value)))


def get_results_from_url(url, artist='Unknown Artist'):
    """Download url and parse videos. Youtube channels don't show an artist so
    you can provide one with the artist arument."""
    r = get(url)
    if not r.ok:
        raise ValueError('Error %d.' % r.status_code)  # Something went wrong.
    logger.info('URL: %s.', r.url)
    s = BeautifulSoup(r.content, 'html.parser')
    results = s.find_all(attrs={'class': 'yt-uix-tile-link'})
    logger.info('Results: %d.', len(results))
    videos = []
    for vid in results:
        vid_url = vid['href']
        if not vid_url.startswith('http'):
            if vid_url.startswith('/user') or vid_url.startswith('/channel'):
                logger.info('Adding channel %s.', vid.text)
                videos.append(YoutubeChannel(vid.text, vid_url))
                continue
            vid_url = urljoin(video_url, vid_url)
        vid_artist = vid.parent.parent.find(attrs={'class': 'g-hovercard'})
        if vid_artist is None:
            vid_artist = artist
        else:
            vid_artist = vid_artist.text
        video = YoutubeTrack(
            vid_artist,
            None, None, vid.text,
            url=vid_url
        )
        videos.append(video)
    return videos
