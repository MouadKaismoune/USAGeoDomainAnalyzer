from __future__ import annotations

import webbrowser

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from app.core.config import CONFIG
from app.core.contact import contact_links
from app.core.icons import load_icon
from app.ui.themes.theme import Theme

_CONTACT_LINKS = contact_links()
_CONTACT_ICONS = (
    ("linkedin", "LinkedIn"),
    ("github", "GitHub"),
    ("email", "Email"),
)
_ICON_SIZE = 16


class Footer(QFrame):
    """Bottom bar: app info, developer credit, and contact icon buttons."""

    def __init__(self, theme: Theme, parent=None) -> None:
        super().__init__(parent)
        self._theme = theme
        self.setObjectName("Footer")
        self.setFixedHeight(CONFIG.footer_height)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        self._left = QLabel(CONFIG.name)
        self._left.setObjectName("FooterText")
        layout.addWidget(self._left)

        layout.addStretch(1)

        self._contact_buttons: list[QPushButton] = []
        for icon, tip in _CONTACT_ICONS:
            button = QPushButton()
            button.setObjectName("FooterIcon")
            button.setIconSize(QSize(_ICON_SIZE, _ICON_SIZE))
            button.setFixedSize(26, 26)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setToolTip(tip)
            button.setProperty("_icon_name", icon)
            button.clicked.connect(lambda _=False, name=icon: self._open_contact(name))
            layout.addWidget(button)
            self._contact_buttons.append(button)

        layout.addSpacing(8)

        self._developer = QLabel(f"Made by {CONFIG.developer}")
        self._developer.setObjectName("FooterText")
        layout.addWidget(self._developer)

        self.apply_theme(theme)

    def apply_theme(self, theme: Theme) -> None:
        self._theme = theme
        for button, (icon_name, _) in zip(self._contact_buttons, _CONTACT_ICONS):
            button.setIcon(load_icon(icon_name, theme.text_secondary))

    def _open_contact(self, name: str) -> None:
        url = _CONTACT_LINKS.get(name)
        if url:
            webbrowser.open(url)

    def retranslate(self) -> None:
        self._left.setText(CONFIG.name)
        self._developer.setText(f"Made by {CONFIG.developer}")