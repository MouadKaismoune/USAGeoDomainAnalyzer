from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class BasePage(QWidget):
    """Generic page shell with a title, subtitle, and content area."""

    def __init__(self, title: str, subtitle: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Page")

        self._title = QLabel(title)
        self._title.setObjectName("PageTitle")

        self._subtitle = QLabel(subtitle)
        self._subtitle.setObjectName("PageSubtitle")
        self._subtitle.setWordWrap(True)

        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(12)

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(28, 24, 28, 24)
        page_layout.setSpacing(6)
        page_layout.addWidget(self._title)
        page_layout.addWidget(self._subtitle)
        page_layout.addSpacing(14)
        page_layout.addLayout(self._content_layout, 1)

    def add_content(self, widget: QWidget, stretch: int = 0) -> None:
        self._content_layout.addWidget(widget, stretch)