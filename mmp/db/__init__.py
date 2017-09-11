"""The database portion of the client."""

from .base import Base
from .session import Session, session
from .hotkeys import Section, Hotkey

Base.metadata.create_all()

with session() as s:
    s.query(Section).delete()  # Clear sections.
    s.query(Hotkey).update({'active': False})

__all__ = [
    'Base', 'Session', 'session', 'Hotkey', 'Section'
]
