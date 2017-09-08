"""Provides the RightPanel class."""

from sys import version
import wx
from jinja2 import Environment
from ... import app

info_format = """{{ app.name }} V{{ app.version }}
{{ app.description }}

Python version: {{ python_version }}

Authors:
{% for author in app.authors %}{{ author }}{% endfor %}

Backends: {% for backend in frame.backends %}
{{ backend.name }}
{% else %}
None loaded.
{% endfor %}"""

environment = Environment()


class RightPanel(wx.Panel):
    """This panel is shwon when the root of the tree is focused."""

    def __init__(self, *args, **kwargs):
        """Show the user info about the program."""
        super(RightPanel, self).__init__(*args, **kwargs)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(wx.StaticText(self, label='&Information'), 0, wx.GROW)
        self.info = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE)
        s.Add(self.info, 1, wx.GROW)
        self.SetSizerAndFit(s)
        self.Bind(wx.EVT_SHOW, self.on_show)

    def on_show(self, event=None):
        """Show the panel and populate self.info."""
        if event is not None:
            event.Skip()
        template = environment.from_string(info_format)
        try:
            value = template.render(
                app=app, python_version=version,
                frame=self.GetParent().GetParent()
            )
            self.info.SetValue(value)
        except RuntimeError:
            pass  # Panel no longer exists."""
