"""Provides the Backend class, as well as the make_backend function."""

import logging
import os
import os.path
from enum import Enum
from datetime import datetime
from requests import get
from attr import attrs, attrib, Factory
from simpleconf import Section
from . import app
from .jobs import add_job
from .ui.panels.backend_panel import BackendPanel
from .config import config
from .db import session, File

logger = logging.getLogger(__name__)


class DownloadStates(Enum):
    none = 0
    downloading = 1
    downloaded = 2


class DownloadError(Exception):
    """Download error."""


class AlreadyDownloadingError(DownloadError):
    """This file is already downloading."""


class DownloadFailedError(DownloadError):
    """The download failed."""

    def __init__(self, code, *args, **kwargs):
        self.code = code
        super(DownloadFailedError, self).__init__(*args, **kwargs)


class BackendError(Exception):
    pass


@attrs
class Backend:
    """A backend for playing music."""

    frame = attrib()
    short_name = attrib()
    name = attrib()
    description = attrib()
    loop_func = attrib()
    config = attrib()
    on_search = attrib()
    panel = attrib()
    root = attrib(default=Factory(lambda: None))
    node = attrib(default=Factory(lambda: None), init=False)
    module = attrib(default=Factory(lambda: None), init=False)

    def __attrs_post_init__(self):
        """Start loop_func if it's not None."""
        if self.config is not None:
            if self.config.title == Section.title:
                self.config.title = self.name
            config.backends.add_section(self.short_name, self.config)
            self.frame.add_config(self.frame.backends_config_root, self.config)
        if self.root is None:
            self.root = self.frame.backends_root
        self.panel = self.panel(self, self.frame.splitter)
        self.panel.Hide()
        if self.loop_func is not None:
            add_job(self.name, self.loop)

    @classmethod
    def from_module(cls, frame, module):
        """Return a Backend instance made from a module. The Backend instance
        will have a frame attribute which is the main frame of the
        application."""
        if hasattr(module, 'name'):
            b = cls(
                frame, module.__name__, module.name, getattr(
                    module, 'description', ''
                ),
                getattr(module, 'loop_func', None),
                getattr(module, 'config', None),
                getattr(module, 'on_search', frame.on_error),
                getattr(module, 'BackendPanel', BackendPanel)
            )
            module.backend = b
            return b
        else:
            raise BackendError(
                'The backend loaded from %r has no name.' % module
            )

    def get_download_path(self):
        """Returns the path which should be used for file storage by this
        backend."""
        p = os.path.join(app.media_dir, self.short_name)
        if not os.path.isdir(p):
            os.makedirs(p)
        return p

    def get_full_path(self, name):
        """Get the full path name to the file named name."""
        return os.path.join(self.get_download_path(), name)

    def register_file(self, path):
        """Register a file as present on the system."""
        with session() as s:
            q = s.query(File).filter_by(path=path)
            if q.count():
                f = q.first()
            else:
                f = File(path=path)
            f.downloaded = datetime.utcnow()
            s.add(f)
            c = s.query(File).count()
            if c > config.files['max_files']:
                l = c - config.files['max_files']
                logger.info(
                    'Deleting %d old %s.', l, 'file' if l == 1 else 'files'
                )
                for old in s.query(File).order_by(File.downloaded).limit(l):
                    logger.info('Deleting file %r.', old)
                    if os.path.exists(old.path):
                        try:
                            os.remove(old.path)
                        except OSError as e:
                            logger.warning('Unable to delete %s:', old.path)
                            logger.exception(e)
                    s.delete(old)
            return f.id

    def get_download_state(self, name):
        """Get the state of a file. The value returned will be one of the
        members of DownloadStates."""
        with session() as s:
            q = s.query(File).filter_by(
                path=os.path.join(self.get_download_path(), name)
            ).first()
            if q is None:
                return DownloadStates.none
            elif q.downloaded is None:
                return DownloadStates.downloading
            else:
                return DownloadStates.downloaded

    def download_file(self, url, name, overwrite=False, **kwargs):
        """Download the given URL to the specified filename and register the
        file. This method will block. If overwrite evaluates to True and the
        path already exists, this method does nothing except return the full
        path. Otherwise the file is overwritten if necessary before the path is
        returned. All extra kwargs are passed onto requests.get."""
        path = self.get_full_path(name)
        if not os.path.isfile(path) or overwrite:
            if self.get_download_state(name) is DownloadStates.downloading:
                raise AlreadyDownloadingError()
            with session() as s:
                f = s.query(File).filter_by(path=path).first()
                if f is None:
                    f = File(path=path)
                f.downloaded = None
                s.add(f)
                s.commit()
                logger.info('Downloading %s to %s.', url, f.path)
                r = get(url, **kwargs)
                if not r.ok:
                    raise DownloadFailedError(r.status_code)
                if r.content.__class__ is bytes:
                    flags = 'wb'
                else:
                    flags = 'w'
                with open(path, flags) as fp:
                    fp.write(r.content)
                f.downloaded = datetime.now()
                s.add(f)
        return path
