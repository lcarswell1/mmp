"""Provides the main program configuration."""

import os.path
from simpleconf import Section, Option
from simpleconf.validators import Integer
from . import app


class Config(Section):
    """Program configuration."""
    filename = os.path.join(app.data_dir, 'config.json')
    title = 'Options'

    class sound(Section):
        title = 'Sound'

        crossfade_amount = Option(
            0, title='The time to spend crossfading between songs',
            validator=Integer(min=0)
        )
        option_order = [crossfade_amount]

    class backends (Section):
        title = 'Backends'


config = Config(load=False)  # Load later.

__all__ = ['config']
