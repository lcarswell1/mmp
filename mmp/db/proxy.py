"""Provides the DBProxy class."""

from attr import attrs, attrib, Factory


@attrs
class DBProxy:
    """Represents an entry in one of the database tables."""

    cls = attrib()
    id = attrib()
    panel = attrib(default=Factory(lambda: None), init=False)
