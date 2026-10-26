"""Shared TUI widgets."""

from __future__ import annotations

from textual.binding import Binding
from textual.containers import ItemGrid
from textual.widgets import Input, Static


class StatusBar(Static):
    """Bottom status / hint line."""

    def __init__(self, *args, **kwargs):
        kwargs["markup"] = False
        super().__init__(*args, **kwargs)

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $surface;
        color: $text-muted;
        padding: 0 1;
    }
    """

    def set_status(self, text: str) -> None:
        self.update(text)


class CamouflageInput(Input):
    """Input that yields the boss key to the app instead of inserting `."""

    BINDINGS = [
        Binding("grave_accent", "app.boss", "Boss", priority=True, show=False),
    ]


class ToolBar(ItemGrid):
    """Text actions that wrap into visible, clickable rows in narrow panes."""

    def __init__(self, *children, **kwargs):
        kwargs.setdefault("min_column_width", 14)
        super().__init__(*children, **kwargs)

    DEFAULT_CSS = """
    ToolBar {
        height: auto;
        grid-rows: 1;
        grid-gutter: 0 1;
        padding: 0 1;
        background: transparent;
    }
    ToolBar Button {
        margin: 0;
        min-width: 0;
        height: 1;
    }
    """
