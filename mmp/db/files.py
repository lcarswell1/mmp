"""Files which have been downloaded by the client."""

from sqlalchemy import Column, String, DateTime
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base


@attrs_sqlalchemy
class File(Base):
    """A file object."""
    __tablename__ = 'files'
    path = Column(String(500), nullable=False)
    downloaded = Column(DateTime(timezone=True), nullable=True)
