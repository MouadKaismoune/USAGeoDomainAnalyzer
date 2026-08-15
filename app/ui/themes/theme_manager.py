from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from app.ui.themes.theme import DARK, LIGHT, Theme


class ThemeManager(QObject):
    theme_changed = Signal(Theme)

    def __init__(self, initial_theme: Theme = LIGHT, parent=None) -> None:
        super().__init__(parent)
        self._theme = initial_theme

    @property
    def current_theme(self) -> Theme:
        return self._theme

    def set_theme(self, theme: Theme) -> None:
        if theme is self._theme:
            return
        self._theme = theme
        self.theme_changed.emit(theme)

    def toggle(self) -> None:
        self.set_theme(DARK if self._theme is LIGHT else LIGHT)
