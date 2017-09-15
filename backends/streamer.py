"""Allows you to stream from URLs."""

import logging
from urllib.request import Request, urlopen
from attr import attrs, attrib, Factory
from bs4 import BeautifulSoup
from requests import get
from sound_lib.main import BassError
from sound_lib.stream import URLStream
from mmp.tracks import Track
from mmp.jobs import add_job
from mmp import sound

logger = logging.getLogger(__name__)

name = 'Streamer'
description = 'Extract audio streams from web pages or play streams directly.'
backend = None


@attrs
class StreamerTrack(Track):

    url = attrib(default=Factory(lambda: None))

    def __attrs_post_init__(self):
        self.title = self.url

    def get_stream(self):
        return URLStream(self.title.encode())


def set_stream_title():
    """Code modified from:
    http://stackoverflow.com/questions/6613587/reading-shoutcast-icecast-
    metadata-from-a-radio-stream-with-python"""
    if sound.new_stream is None or not isinstance(
        sound.new_stream.track, StreamerTrack
    ):
        return
    stream = sound.new_stream.track
    request = Request(stream.url)
    request.add_header('Icy-MetaData', 1)
    response = urlopen(request)
    icy_metaint_header = response.headers.get('icy-metaint')
    if icy_metaint_header is not None:
        metaint = int(icy_metaint_header)
        read_buffer = metaint+256
        content = response.read(read_buffer)
        title = content[metaint:].split("'".encode())[1].decode()
        if title != stream.title:
            stream.title = title
            backend.panel.results.SetString(stream.index, stream.title)


def on_init(backend):
    add_job('Set Stream Title', set_stream_title, run_every=1.0)


def on_search(value):
    if '://' not in value:
        value = 'http://' + value
    results = []
    try:
        s = URLStream(value.encode())
        results.append(StreamerTrack(None, None, None, None, url=value))
    except BassError:
        # Probably a web page. Let's see what we can see.
        r = get(value)
        s = BeautifulSoup(r.content)
        for audio in s.find_all('audio'):
            for source in audio.find_all('source'):
                results.append(
                    StreamerTrack(None, None, None, None, url=source['src'])
                )
    return results
