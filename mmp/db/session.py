"""Provides the scoped session."""

from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, scoped_session
from .engine import engine

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


@contextmanager
def session():
    """Close the session when we're done."""
    s = Session()
    try:
        yield s
        s.commit()
    except Exception as e:
        s.rollback()
        raise e
    finally:
        Session.remove()
