"""Provides the Hotkey class."""

import six
import wx
from attr import attrs, attrib


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


def add_hotkey(control, modifiers, key, func, id=None):
    """Add a hotkey to the specified control. You can either specify key as an
    integer or a string which will be passed through ord. If id is None a new
    ID will be generated."""
    if id is None:
        id = wx.NewId()
    control.Bind(wx.EVT_MENU, func, id=id)
    h = Hotkey(modifiers, key, func, id, control)
    l = hotkeys.get(control, [])
    l.append(h)
    hotkeys[control] = l
    rebuild_accelerator_table(control)


def rebuild_accelerator_table(control):
    """Rebuild the accelerator tables for control from the list of defined
    hotkeys."""
    tbl = []
    for hotkey in hotkeys.get(control, []):
        tbl.append((hotkey.modifiers, hotkey.key, hotkey.id))
    control.SetAcceleratorTable(wx.AcceleratorTable(tbl))
