"""Provides the Hotkey class."""

import logging
import six
from sqlalchemy import and_, or_
from .db import session, Hotkey, Section

logger = logging.getLogger(__name__)
functions = {}

# Hotkey sections.
with session() as s:
    for var, name in (
        ('main', 'Main'),
        ('media', 'Media'),
    ):
        section = Section(name=name)
        s.add(section)
        s.commit()
        locals()['section_%s' % var] = section.id
    del section


def add_section(name, parent_id=None):
    """Return a section named name as a subsection of the Section instance with
    the id of parent_id."""
    with session() as s:
        section = s.query(Section).filter_by(
            name=name, parent_id=parent_id
        ).first()
        if section is None:
            section = Section(name=name, parent_id=parent_id)
        s.add(section)
        s.commit()
        return section.id


def handle_hotkey(event):
    """Handle an incoming hotkey."""
    key = event.GetKeyCode()
    modifiers = event.GetModifiers()
    with session() as s:
        l = s.query(Hotkey).filter(
            and_(
                or_(
                    and_(
                        Hotkey.key == key,
                        Hotkey.modifiers == modifiers
                    ),
                    and_(
                        Hotkey.key.is_(None),
                        Hotkey.default_key == key,
                        Hotkey.modifiers.is_(None),
                        Hotkey.default_modifiers == modifiers
                    )
                ),
                or_(
                    Hotkey.control_id.is_(None),
                    Hotkey.control_id == event.EventObject.GetId()
                )
            )
        )
        if not l.count():
            return event.Skip()
        for hotkey in l:
            logger.info('Running %r.', hotkey)
            functions[
                (hotkey.control_id, hotkey.func_name)
            ](event)
            if event.Skipped:
                logger.info('Done.')
                break  # Stop execution.


def add_hotkey(key, func, modifiers=0, control=None, section_id=1):
    """Add a hotkey bound to key with optional modifiers. If control is not
    None the key will only work when that control has focus, otherwise it is
    global to the application. If section is not provided the top-level section
    will be assumed."""
    if control is not None:
        control = control.GetId()
    if isinstance(key, six.string_types):
        key = ord(key)
    with session() as s:
        kwargs = dict(
            default_modifiers=modifiers, default_key=key,
            func_name=func.__name__, section_id=section_id
        )
        q = s.query(Hotkey).filter_by(**kwargs)
        if q.count():
            hotkey = q.first()
            logger.info('Found hotkey %r.', hotkey)
        else:
            hotkey = Hotkey(**kwargs)
            logger.info('Registered hotkey %r.', hotkey)
        hotkey.control_id = control
        hotkey.active = True
        functions[(hotkey.control_id, hotkey.func_name)] = func
        s.add(hotkey)
