"""Provides the Base class."""

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from .engine import engine
from .session import session


class _Base:
    """The base class for Base."""
    id = Column(Integer, primary_key=True)

    def save(self):
        """Save this object."""
        with session() as s:
            s.add(self)

    def delete(self):
        """Delete this object."""
        with session() as s:
            s.delete(self)


Base = declarative_base(cls=_Base, bind=engine)
