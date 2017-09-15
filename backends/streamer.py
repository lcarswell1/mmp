"""Allows you to stream from URLs."""

import logging
from bs4 import BeautifulSoup
from requests import get
from sound_lib.main import BassError
from sound_lib.stream import URLStream
from mmp.tracks import Track

logger = logging.getLogger(__name__)

name = 'Streamer'
description = 'Extract audio streams from web pages or play streams directly.'


class StreamerTrack(Track):
    def get_stream(self):
        return URLStream(self.title.encode())


def on_search(value):
    results = []
    try:
        s = URLStream(value.encode())
        results.append(StreamerTrack(None, None, None, value))
    except BassError:
        # Probably a web page. Let's see what we can see.
        r = get(value)
        s = BeautifulSoup(r.content)
        for audio in s.find_all('audio'):
            for source in audio.find_all('source'):
                results.append(StreamerTrack(None, None, None, source['src']))
    return results
