"""A Google Play Music backend."""

import os
import os.path
import logging
from datetime import timedelta
import wx
from sound_lib.stream import URLStream
from attr import attrs, attrib, Factory
from gmusicapi import Mobileclient
from simpleconf import Section, Option
from leatherman.tracks import Track
from leatherman.app import media_dir

logger = logging.getLogger(__name__)

data_dir = None

downloading = []


name = "Google Play Music"
api = Mobileclient()
backend = None
authenticated = False


def on_init(backend):
    global data_dir
    data_dir = os.path.join(media_dir, 'Google')
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)


def get_id(d):
    """Get the id from a dictionary d."""
    return d.get('storeId', d.get('nid', d.get('trackId', d.get('id'))))


@attrs
class GoogleTrack(Track):
    """A track from Google."""
    duration = attrib(default=Factory(timedelta))
    id = attrib(default=Factory(lambda: None))

    def get_stream(self):
        """Check this track has been downloaded first."""
        assert self.id is not None
        return URLStream(
            api.get_stream_url(self.id).encode()
        )

    @classmethod
    def from_dict(cls, data):
        """Create a Track instance from a track dictionary from Google."""
        return cls(
            data.get('artist', 'Unknown Artist'),
            data.get('album', 'Unknown Album'),
            data.get('trackNumber', 0),
            data.get('title', 'Unknown Title'),
            duration=timedelta(
                milliseconds=int(data.get('durationMillis', '0'))
            ),
            id=get_id(data)
        )


def try_login():
    global authenticated
    if authenticated:
        logger.info('Already logged in.')
        return  # Already logged in.
    authenticated = api.login(
        config.login['username'], config.login['password'],
        api.FROM_MAC_ADDRESS
    )
    if not authenticated:
        logger.info('Failed login.')
        raise RuntimeError(
            'Login failed. Check your username and password and try again.'
        )
    logger.info('Login successful.')


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
        logger.info('Not searching with an empty value.')
        return False
    try_login()
    results = api.search(value)
    for key, value in results.items():
        logger.info('%s: %d.', key, len(value))
    songs = results['song_hits']
    tracks = []
    for data in songs:
        tracks.append(GoogleTrack.from_dict(data['track']))
    backend.panel.add_results(tracks)
    return True
