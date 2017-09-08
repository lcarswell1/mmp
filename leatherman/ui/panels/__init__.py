"""The panels."""

from .left_panel import LeftPanel
from .right_panel import RightPanel

__all__ = []

for p in (
    LeftPanel, RightPanel
):
    __all__.append(p.__name__)
