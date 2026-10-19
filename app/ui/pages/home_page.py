from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QVBoxLayout

from translator import translator as t
from app.ui.components.stat_card import StatCard
from app.ui.pages.base_page import BasePage
from app.ui.themes.theme import Theme

_FIELDS = (
    ("cities", "cities", "primary"),
    ("niches", "niches", "primary"),
    ("domains", "domains", "primary"),
    ("available", "check", "success"),
    ("registered", "lock", "error"),
    ("unknown", "question", "warning"),
    ("checked", "checkcheck", "success"),
    ("unchecked", "clock", "warning"),
)

_LABELS = {
    "cities": "home_total_cities",
    "niches": "home_total_niches",
    "domains": "home_total_domains",
    "available": "home_available",
    "registered": "home_registered",
    "unknown": "home_unknown",
    "checked": "home_checked",
    "unchecked": "home_unchecked",
}


class HomePage(BasePage):
    """Dashboard screen with live database statistics."""

    def __init__(self, parent=None) -> None:
        super().__init__(
            t.t("home_title"),
            t.t("home_subtitle"),
            parent,
        )
        self._cards: dict[str, StatCard] = {}
        self._theme: Theme | None = None
        self.add_content(self._build_stats_grid())
        self._content_layout.addStretch(1)

    def _build_stats_grid(self) -> QFrame:
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        for index, (field, icon, accent) in enumerate(_FIELDS):
            row, col = divmod(index, 4)
            card = StatCard(icon, accent=accent, caption=t.t(_LABELS[field]))
            grid.addWidget(card, row, col)
            self._cards[field] = card

        container = QFrame()
        container.setObjectName("CardGrid")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 8, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addLayout(grid)
        return container

    def refresh(self) -> None:
        from moduls.cities.services import get_city_count
        from moduls.niches.services import get_checked_count, get_niche_count, get_unchecked_count
        from moduls.domains.services import get_status_counts

        status = get_status_counts()
        values = {
            "cities": str(get_city_count()),
            "niches": str(get_niche_count()),
            "domains": str(status["available"] + status["registered"] + status["unknown"]),
            "available": str(status["available"]),
            "registered": str(status["registered"]),
            "unknown": str(status["unknown"]),
            "checked": str(get_checked_count()),
            "unchecked": str(get_unchecked_count()),
        }
        for field, card in self._cards.items():
            card.set_value(values.get(field, "0"))

    def apply_theme(self, theme: Theme) -> None:
        self._theme = theme
        for card in self._cards.values():
            card.apply_theme(theme)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.refresh()