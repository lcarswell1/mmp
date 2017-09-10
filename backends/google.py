"""A Google Play Music backend."""

import os
import os.path
import logging
from time import time
from functools import partial
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
        self.search_field.Disable()

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
    pass


class LibraryPanel(GooglePanel):
    """A panel to display the contents of the library."""
    pass


def add_tracks(tracks, panel):
    if not tracks:
        return True  # Stop.
    track = tracks.pop(0)
    wx.CallAfter(panel.add_result, track)


def build_playlists():
    """Get playlists from Google and add them to playlists_root."""
    playlists.clear()
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

    def finalise_playlists():
        """Only start when all playlists have been loaded."""
        if len(playlists) == num_playlists:  # Let's go.
            logger.info('Loading playlist tracks...')
            playlist_tracks = []

            def finish():
                """Load all entries from playlist_tracks."""
                if not playlist_tracks:
                    return True
                backend, tracks = playlist_tracks.pop(0)
                backend.panel.add_results(tracks)

            for backend, data in playlists:
                logger.info(
                    'Loading tracks for the %s playlist.', backend.name
                )
                tracks = [
                    GoogleTrack.from_dict(
                        x['track']
                    ) for x in data if 'track' in x
                ]
                logger.info('Tracks: %d.', len(tracks))
                playlist_tracks.append((backend, tracks))
            add_job('Load Playlist Tracks', finish, run_every=load_speed)
            return True

    add_job('Finalise playlists', finalise_playlists)
    add_job('Add Playlists', add_playlists, run_every=load_speed)
    return True


def add_playlist(playlist):
    """Add a single playlist."""
    started = time()
    name = playlist['name']
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
    backend.frame.add_backend(b)
    b.playlist_id = playlist['id']
    playlists.append((b, playlist['tracks']))
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
    tracks = [GoogleTrack.from_dict(x) for x in l]
    add_job(
        'Add library tracks',
        partial(add_tracks, tracks, library_backend.panel),
        run_every=load_speed
    )
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
