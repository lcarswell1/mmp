"""Play music from soma.fm."""

import logging
from configparser import SafeConfigParser
import wx
from requests import get
from bs4 import BeautifulSoup
from attr import attrs, attrib, Factory
from sound_lib.stream import URLStream
from mmp.backends import BackendError
from mmp.tracks import Track

logger = logging.getLogger(__name__)

name = 'Soma'
description = 'Commercial-free, Listener-supported Radio.'
backend = None
base_url = "http://somafm.com"
stream_url = 'http://somafm.com/play'


class SomaError(Exception):
    pass


@attrs
class SomaTrack(Track):
    """Add a URL."""

    url = attrib(default=Factory(lambda: None))

    def get_stream(self):
        """Get the stream associated with this station."""
        url = stream_url + self.url
        logger.info('Downloading stream information from %s.', url)
        r = get(url)
        if not r.ok:
            raise SomaError('%d error.' % r.status_code)
        scp = SafeConfigParser()
        scp.read_string(r.content.decode())
        section = scp['playlist']
        n = section.getint('numberofentries')
        for i in range(n):
            key = 'File%d' % n
            try:
                return URLStream(section.get(key).encode())
            except Exception as e:
                logger.warning('Failed to get %s of %r:', key, section)
                logger.exception(e)
        logger.critical(
            'No stream URL found in %d entries for station %r.', n, self
        )
        raise SomaError('No stream URL found.')


def load_stations(event):
    """Called when the panel is shown and there are no results yet."""
    if backend.panel.results.Count:
        return  # Don't parse again.
    r = get(base_url)
    if not r.ok:
        raise BackendError('Error %d.' % r.statuscode)
    s = BeautifulSoup(r.content, 'html.parser')
    results = []
    for station in s.findAll('li', {"class": "cbshort"}):
        results.append(
            SomaTrack(
                None, None, None, station.find('a').find('img')['alt'],
                url=station.find('a')['href'].rstrip('/')
            )
        )
    backend.panel.add_results(results)


def on_init(backend):
    backend.panel.search_field.Disable()
    backend.panel.Bind(wx.EVT_SHOW, load_stations)
