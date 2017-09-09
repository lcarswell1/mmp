"""Provides the main program configuration."""

import os.path
from simpleconf import Section, Option
from simpleconf.validators import Integer
from . import app


class TrackFormatOption(Option):
    def set(self, value):
        super(TrackFormatOption, self).set(value)
        app.frame.track_format_template = app.environment.from_string(value)


class Config(Section):
    """Program configuration."""
    filename = os.path.join(app.data_dir, 'config.json')
    title = 'Options'

    class interface(Section):
        """Change aspects of the interface."""

        title = 'Interface'

        track_format = TrackFormatOption(
            '{{ artist }} - {{ album }} - {{ number }} - {{ title}} ({{ '
            'duration | format_timedelta }} *{{ backend.name }}*',
            title='&Result Format'
        )
        last_backend = Option('', title='The last &Backend to be viewed')

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
