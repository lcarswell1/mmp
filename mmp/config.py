"""Provides the main program configuration."""

import os.path
from simpleconf import Section, Option
from simpleconf.validators import Integer, Float
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
            '{{ artist }} - '
            '{{ album }} - '
            '{{ number }} - '
            '{{ title}} '
            '{% if duration is defined %}({{ duration | format_timedelta }}) '
            '{% endif %}*{{ backend.name }}*',
            title='&Result Format'
        )
        last_backend = Option('', title='The last &Backend to be viewed')

    class sound(Section):
        title = 'Sound'

        volume = Option(100, validator=Integer(min=0, max=100))
        crossfade_amount = Option(
            0, title='The time to spend crossfading between songs',
            validator=Integer(min=0)
        )
        move_amount = Option(10000, title='Move &Amount', validator=Integer)
        volume_base = Option(
            10.0, title='&Volume Logarithm Base',             validator=Float(
                min=1.00001, max=100.0
            )
        )
        volume_adjust = Option(
            2, title='Volume &Sensativity', validator=Integer(min=1, max=100)
        )
        option_order = [
            crossfade_amount, move_amount, volume_base, volume_adjust
        ]

    class backends (Section):
        title = 'Backends'


config = Config(load=False)  # Load later.

__all__ = ['config']
