from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from app.ui.pages.base_page import BasePage


class ReportsPage(BasePage):
    def __init__(self, parent=None) -> None:
        super().__init__(
            "Reports",
            "Placeholder page for displaying reports.",
            parent,
        )
        self.add_content(self._build_reports_card(), 1)

    def _build_reports_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        title = QLabel("Reports")
        title.setObjectName("CardTitle")
        layout.addWidget(title)

        text = QLabel(
            "This placeholder page will be replaced with report content "
            "when the template is adapted for a specific application."
        )
        text.setObjectName("CardText")
        text.setWordWrap(True)
        layout.addWidget(text)
        return card