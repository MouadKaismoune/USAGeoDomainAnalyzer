from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from app.core.icons import load_icon_pixmap
from app.ui.themes.theme import Theme

_ACCENTS = ("primary", "success", "warning", "error")


class StatCard(QFrame):
    """A reusable, theme-aware dashboard stat card.

    Displays an icon badge, a large value, and a caption label. The accent
    determines the badge tint and the value color.
    """

    def __init__(
        self,
        icon_name: str,
        accent: str = "primary",
        caption: str = "",
        fallback_value: str = "0",
        parent=None,
    ) -> None:
        super().__init__(parent)
        if accent not in _ACCENTS:
            accent = "primary"
        self._icon_name = icon_name
        self._accent = accent

        self.setObjectName("StatCard")
        self.setProperty("accent", accent)
        self.setMinimumHeight(96)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        self._badge = QLabel()
        self._badge.setObjectName("StatBadge")
        self._badge.setProperty("accent", accent)
        self._badge.setFixedSize(44, 44)
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._badge, alignment=Qt.AlignmentFlag.AlignVCenter)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        self._value = QLabel(fallback_value)
        self._value.setObjectName("StatValue")
        self._value.setProperty("accent", accent)
        text_col.addWidget(self._value)

        self._caption = QLabel(caption)
        self._caption.setObjectName("StatCaption")
        text_col.addWidget(self._caption)

        layout.addLayout(text_col)
        layout.addStretch(1)

    def set_value(self, text: str) -> None:
        self._value.setText(text)

    def apply_theme(self, theme: Theme) -> None:
        """Refresh the badge icon so it picks up the current theme palette."""
        color = _accent_color(theme, self._accent)
        self._badge.setPixmap(load_icon_pixmap(self._icon_name, color, 22))


def _accent_color(theme: Theme, accent: str) -> str:
    color = getattr(theme, accent, None)
    if color:
        return color
    return theme.primary