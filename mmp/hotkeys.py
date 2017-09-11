"""Provides the Hotkey class."""

import logging
import six
from sqlalchemy import and_, or_
from .db import Session, session, Hotkey, Section
logger = logging.getLogger()
functions = {}


def get_section(name='General', parent=None):
    """Return a section named name as a subsection of parent. This Section
    instance will not be bound to a session. If name is not provided return the
    top-level section."""
    section = Session.query(Section).filter_by(
        name=name, parent=parent
    ).first()
    if section is None:
        section = Section(name=name, parent=parent)
    return section


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


def add_hotkey(key, func, modifiers=0, control=None, section=None):
    """Add a hotkey bound to key with optional modifiers. If control is not
    None the key will only work when that control has focus, otherwise it is
    global to the application."""
    if control is not None:
        control = control.GetId()
    if isinstance(key, six.string_types):
        key = ord(key)
    with session() as s:
        if section is None:
            section = get_section()
        kwargs = dict(
            default_modifiers=modifiers, default_key=key,
            func_name=func.__name__, control_id=control, section=section
        )
        q = s.query(Hotkey).filter_by(**kwargs)
        if q.count():
            hotkey = q.first()
            hotkey.active = True
            logger.info('Found hotkey %r.', hotkey)
        else:
            hotkey = Hotkey(active=True, **kwargs)
            logger.info('Registered hotkey %r.', hotkey)
        functions[(hotkey.control_id, hotkey.func_name)] = func
        s.add(hotkey)
