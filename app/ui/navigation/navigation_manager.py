from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget

from app.ui.navigation.page_registry import PageRegistry


class NavigationManager(QObject):
    current_page_changed = Signal(str)

    def __init__(self, content_area: QStackedWidget, registry: PageRegistry) -> None:
        super().__init__()
        self._content_area = content_area
        self._registry = registry
        self._pages: dict[str, object] = {}
        self._current_page_id: str | None = None

    def navigate(self, page_id: str) -> None:
        if page_id == self._current_page_id:
            return
        widget = self._pages.get(page_id)
        if widget is None:
            widget = self._registry.create(page_id)
            self._content_area.addWidget(widget)
            self._pages[page_id] = widget
        self._content_area.setCurrentWidget(widget)
        self._current_page_id = page_id
        self.current_page_changed.emit(page_id)
