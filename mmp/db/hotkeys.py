"""Provides the Hotkey and Section classes."""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base


@attrs_sqlalchemy
class Section(Base):
    """A hotkey section."""
    __tablename__ = 'sections'
    name = Column(String(50), nullable=False)
    parent_id = Column(
        Integer, ForeignKey(__tablename__ + '.id'), nullable=True
    )
    parent = relationship(
        'Section', backref='children', foreign_keys=[parent_id],
        remote_side='Section.id'
    )


@attrs_sqlalchemy
class Hotkey(Base):
    """A hotkey definition."""
    __tablename__ = 'hotkeys'
    key = Column(Integer, nullable=True)
    default_key = Column(Integer, nullable=False)
    modifiers = Column(Integer, nullable=True)
    default_modifiers = Column(Integer, nullable=False, default=0)
    func_name = Column(String(50), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    control_id = Column(Integer, nullable=True)
    section_id = Column(Integer, ForeignKey(Section.id), nullable=False)
    section = relationship(Section, backref='hotkeys')
