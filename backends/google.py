"""A Google Play Music backend."""

import os
import os.path
import logging
from time import time
from datetime import timedelta
import wx
from wx.lib.sized_controls import SizedPanel
from sound_lib.stream import URLStream
from attr import attrs, attrib, Factory
from gmusicapi import Mobileclient
from simpleconf import Section, Option
from mmp.tracks import Track
from mmp.app import media_dir
from mmp.jobs import add_job
from mmp.backends import Backend
from mmp.ui.panels.backend_panel import BackendPanel

logger = logging.getLogger(__name__)

data_dir = None
downloading = []


name = "Google Play Music"
api = Mobileclient()
backend = None
authenticated = False
playlists = []
playlists_backend = None
library_backend = None
load_speed = 0.05


class GooglePanel(BackendPanel):
    def __init__(self, *args, **kwargs):
        super(GooglePanel, self).__init__(*args, **kwargs)
        self.processing_tracks = False
        self.tracks_data = None
        self.logger = logging.getLogger(self.backend.name + ' Playlist')
        self.Bind(wx.EVT_SHOW, self.on_show)
        self.search_field.Disable()

    def add_track(self):
        if not self.tracks_data:
            if self.tracks_data is not None:  # Empty list.
                self.logger.info('Tracks loaded.')
            self.tracks_data = None
            self.processing_tracks = False
            return True  # Stop.
        d = self.tracks_data.pop(0)
        track = GoogleTrack.from_dict(d)
        self.logger.info('Loading track %r.', track)
        wx.CallAfter(self.add_result, track)

    def on_show(self, event):
        """Start adding tracks."""
        event.Skip()
        if self.tracks_data and not self.processing_tracks:
            self.processing = True
            add_job(
                'Load tracks for %s' % self.backend.name,
                self.add_track, run_every=load_speed
            )

    def do_search(self, event):
        pass  # Do nothing.


class PlaylistsPanel(SizedPanel):
    def __init__(self, backend, *args, **kwargs):
        self.backend = backend
        super(PlaylistsPanel, self).__init__(*args, **kwargs)
        self.SetSizerType('vertical')
        self.refresh_playlists = wx.Button(self, label='Refresh &Playlists')
        self.refresh_library = wx.Button(self, label='Refresh &Library')
        self.refresh_playlists.Bind(
            wx.EVT_BUTTON, lambda event: add_job(
                'Refresh Playlists', build_playlists
            )
        )
        self.refresh_library.Bind(
            wx.EVT_BUTTON, lambda event: add_job(
                'Refresh Library', build_library
            )
        )


class PlaylistPanel(GooglePanel):
    """A panel for displaying the contents of playlists."""

    def __init__(self, *args, **kwargs):
        self.id = None
        super(PlaylistPanel, self).__init__(*args, **kwargs)


class LibraryPanel(GooglePanel):
    """A panel to display the contents of the library."""
    pass


def build_playlists():
    """Get playlists from Google and add them to playlists_root."""
    playlists.clear()
    logger.info('Loading playlists...')
    if not authenticated:
        try_login()
        return True
    logger.info('Loading playlists...')
    playlists_data = sorted(
        api.get_all_user_playlist_contents(),
        key=lambda entry: entry.get('name', 'Untitled Playlist')
    )
    num_playlists = len(playlists_data)
    logger.info('Loaded playlists: %d.', num_playlists)

    def add_playlists():
        """Add playlists."""
        if not playlists_data:
            return True
        playlist = playlists_data.pop(0)
        wx.CallAfter(add_playlist, playlist)

    add_job('Add Playlists', add_playlists, run_every=load_speed)
    return True


def add_playlist(playlist):
    """Add a single playlist."""
    started = time()
    name = playlist['name']
    id = playlist['id']
    if id in playlists:
        return False  # Go to the next one.
    b = Backend(
        backend.frame,  # Frame.
        backend.short_name,  # Short name.
        name,  # Long name.
        playlist.get('description', 'No description available'),
        None,  # Loop function.
        None,  # Configuration.
        lambda value: None,  # Search function.
        PlaylistPanel,  # Panel.
        root=playlists_backend.node
    )
    b.panel.id = id
    b.panel.tracks_data = [x['track'] for x in playlist.get('tracks', [])]
    backend.frame.add_backend(b)
    logger.info(
        'Loaded the %s playlist in %g seconds.', b.name, time() - started
    )


def build_library():
    """Get the contents of the user library and show it in the library
    panel."""
    if not authenticated:
        try_login()
        return True
    logger.info('Retrieving library.')
    l = api.get_all_songs()
    logger.info('Library tracks: %d.', len(l))
    library_backend.panel.tracks_data = l
    return True


def on_init(backend):
    global data_dir, playlists_backend, library_backend
    data_dir = os.path.join(media_dir, 'Google')
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    playlists_backend = Backend(
        backend.frame,  # Frame.
        backend.short_name + '_playlists',  # Short name.
        'Playlists',  # Long name.
        'Your Google Music playlists.',  # Description.
        None,  # Loop function.
        None,  # Configuration.
        lambda value: None,  # Search function.
        PlaylistsPanel,  # Panel.
        root=backend.node
    )
    library_backend = Backend(
        backend.frame,  # Frame.
        backend.short_name + '_library',  # Short name.
        'Library',  # Name.
        'Your Google Music library.',  # Description.
        None,  # Loop Function.
        None,  # Configuration.
        lambda text: None,  # Search function.
        LibraryPanel,  # Panel.
        root=backend.node
    )
    backend.frame.add_backend(playlists_backend)
    backend.frame.add_backend(library_backend)


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
    add_job('Populate Google Playlists', build_playlists)
    add_job('Populate Google Library', build_library)


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
    try_login()
    results = api.search(value)
    for key, value in results.items():
        logger.info('%s: %d.', key, len(value))
    songs = results['song_hits']
    tracks = []
    for data in songs:
        tracks.append(GoogleTrack.from_dict(data['track']))
    return tracks
