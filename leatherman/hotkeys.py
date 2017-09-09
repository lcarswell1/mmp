"""Provides the Hotkey class."""

import six
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
