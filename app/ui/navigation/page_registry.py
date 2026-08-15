from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

PageFactory = Callable[[], QWidget]


class PageRegistry:
    """Maps stable page identifiers to page factories."""

    def __init__(self) -> None:
        self._factories: dict[str, PageFactory] = {}

    def register(self, page_id: str, factory: PageFactory) -> None:
        if page_id in self._factories:
            raise ValueError(f"Page '{page_id}' is already registered.")
        self._factories[page_id] = factory

    def create(self, page_id: str) -> QWidget:
        factory = self._factories.get(page_id)
        if factory is None:
            return self._create_unknown_page(page_id)
        return factory()

    def contains(self, page_id: str) -> bool:
        return page_id in self._factories

    def _create_unknown_page(self, page_id: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel(f"Unknown page: {page_id}"))
        return widget
