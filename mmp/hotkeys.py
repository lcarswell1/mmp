"""Provides the Hotkey class."""

import logging
import six
import wx
from attr import attrs, attrib

logger = logging.getLogger()


@attrs
class Hotkey:
    """An accelerator."""

    modifiers = attrib()
    key = attrib()
    func = attrib()
    id = attrib()
    control = attrib()

    def __attrs_post_init__(self):
        if isinstance(self.key, six.string_types):
            self.key = ord(self.key)


hotkeys = {}


def handle_hotkey(event):
    """Handle an incoming hotkey."""
    l = hotkeys.get((event.GetModifiers(), event.GetKeyCode()))
    if not l:
        return event.Skip()
    for hotkey in l:
        if hotkey.control in (None, event.EventObject):
            logger.info('Running %r.', hotkey)
            hotkey.func(event)
            if event.Skipped:
                logger.info('Done.')
                break  # Stop execution.


def add_hotkey(key, func, modifiers=0, control=None, id=None):
    """Add a hotkey bound to key with optional modifiers. If control is not
    None the key will only work when that control has focus, otherwise it is
    global to the application. If id is None a new ID will be generated for
    you."""
    if id is None:
        id = wx.NewId()
    h = Hotkey(modifiers, key, func, id, control)
    key = (h.modifiers, h.key)
    l = hotkeys.get(key, [])
    l.append(h)
    hotkeys[key] = l
