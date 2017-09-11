"""Provides the HotkeyPanel class."""

import wx
from wx.lib.sized_controls import SizedPanel
from ...db import session, Hotkey

keys = {getattr(wx, x): x[4:] for x in dir(wx) if x.startswith('WXK_')}
modifiers = {getattr(wx, x): x[6:] for x in dir(wx) if x.startswith('ACCEL_')}
ignored_keys = (
    wx.WXK_CONTROL, wx.WXK_SHIFT, wx.WXK_START, wx.WXK_TAB, wx.WXK_ALT,
    wx.WXK_WINDOWS_LEFT, wx.WXK_WINDOWS_RIGHT, wx.WXK_NONE
)


class HotkeyPanel(SizedPanel):
    """Set the key for the hotkey attached to this panel."""

    def __init__(self, hotkey_proxy, *args, **kwargs):
        """The provided hotkey_proxy is not the Hotkey instance."""
        self.hotkey_proxy = hotkey_proxy
        super(HotkeyPanel, self).__init__(*args, **kwargs)
        self.SetSizerType('vertical')
        wx.StaticText(self, label='&Hotkey')
        self.hotkey_entry = wx.TextCtrl(
            self, style=wx.TE_READONLY | wx.TE_MULTILINE
        )
        with session() as s:
            hotkey = s.query(Hotkey).get(self.hotkey_proxy.id)
            if hotkey.modifiers is None:
                modifiers = hotkey.default_modifiers
            else:
                modifiers = hotkey.modifiers
            if hotkey.key is None:
                key = hotkey.default_key
            else:
                key = hotkey.key
            self.hotkey_entry.SetValue(self.key_str(modifiers, key))
        self.hotkey_entry.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        wx.Button(
            self, label='&Restore Defaults'
        ).Bind(
            wx.EVT_BUTTON, self.restore_default
        )

    def key_str(self, mods, key):
        """Return a string representing the provided key."""
        res = []
        for value, name in modifiers.items():
            if mods & value:
                res.append(name)
        if key in keys:
            res.append(keys[key])
        else:
            res.append(chr(key))
        return '+'.join(res)

    def on_key(self, event):
        """Set the key."""
        key = event.GetKeyCode()
        if key in ignored_keys:
            return event.Skip()
        mods = event.GetModifiers()
        self.set_key(mods, key)

    def set_key(self, modifiers=None, key=None):
        """Set the contents of the text field and save the updated Hotkey."""
        with session() as s:
            h = s.query(Hotkey).get(self.hotkey_proxy.id)
            if modifiers is None:
                modifiers = h.default_modifiers
            if key is None:
                key = h.default_key
            self.hotkey_entry.SetValue(self.key_str(modifiers, key))
            self.hotkey_entry.SelectAll()
            if key == h.default_key and modifiers == h.default_modifiers:
                h.key = None
                h.modifiers = None
            else:
                h.key = key
                h.modifiers = modifiers
            s.add(h)

    def restore_default(self, event):
        """Restore the default value."""
        self.set_key()
