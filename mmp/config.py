"""Provides the main program configuration."""

import os.path
import logging
from jinja2.exceptions import TemplateError
from simpleconf import Section, Option
from simpleconf.validators import Integer, Float
from . import app

logger = logging.getLogger(__name__)


class TrackFormatOption(Option):
    def set(self, value):
        super(TrackFormatOption, self).set(value)
        try:
            app.track_format_template = app.environment.from_string(value)
        except TemplateError as e:
            logger.warning(
                'Template error:\nOption: %r\nFormat: %r', self, value
            )
            logger.exception(e)
            self.set(self.default)


class TitleFormatOption(Option):
    def set(self, value):
        super(TitleFormatOption, self).set(value)
        app.title_template = app.environment.from_string(value)


class Config(Section):
    """Program configuration."""
    filename = os.path.join(app.data_dir, 'config.json')
    title = 'Options'

    class interface(Section):
        """Change aspects of the interface."""

        title = 'Interface'

        track_format = TrackFormatOption(
            '{% if artist is defined %}{{ artist }} - {% endif %}'
            '{% if album is defined %}{{ album }} - {% endif %}'
            '{% if number is defined %}{{ number }} - {% endif %}'
            '{{ title}} '
            '{% if duration is defined %}({{ duration | format_timedelta }}) '
            '{% endif %}*{{ backend.name }}*',
            title='&Result Format'
        )
        title_format = TitleFormatOption(
            '{{ app_name }} - '
            '{% if playing is not none %}'
            '{{ playing.track.title }} ['
            '{% with stream = playing.stream%}'
            '{% if stream.is_playing %}Playing'
            '{% elif stream.is_paused %}Paused'
            '{% elif stream.is_stopped %}Stopped'
            '{% else %}Unknown State'
            '{% endif %}'
            '{% endwith %}'
            '{% else %}[Nothing Playing'
            '{% endif %}]', title='The format for the window title'
        )
        last_backend = Option('', title='The last &Backend to be viewed')
        option_order = (track_format, title_format)

    class sound(Section):
        title = 'Sound'

        volume = Option(100, validator=Integer(min=0, max=100))
        crossfade_amount = Option(
            0, title='The time to spend crossfading between songs',
            validator=Integer(min=0)
        )
        volume_base = Option(
            10.0, title='&Volume Logarithm Base',             validator=Float(
                min=1.00001, max=100.0
            )
        )
        volume_adjust = Option(
            2, title='Volume &Sensativity', validator=Integer(min=1, max=100)
        )
        option_order = [crossfade_amount, volume_base, volume_adjust]

    class backends (Section):
        title = 'Backends'


config = Config(load=False)  # Load later.

__all__ = ['config']
