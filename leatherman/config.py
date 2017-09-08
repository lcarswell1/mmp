"""Provides the main program configuration."""

import os.path
from simpleconf import Section
from . import app


class Config(Section):
    """Program configuration."""
    filename = os.path.join(app.data_dir, 'config.json')


config = Config()

__all__ = ['config']
