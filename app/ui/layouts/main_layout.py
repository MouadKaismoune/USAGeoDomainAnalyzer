from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from app.core.config import CONFIG
from app.ui.components.footer import Footer
from app.ui.components.header import Header
from app.ui.components.sidebar import Sidebar
from app.ui.navigation.navigation_config import NavigationItem, get_group_labels
from app.ui.navigation.navigation_manager import NavigationManager
from app.ui.themes.theme_manager import ThemeManager

_SHADOW_MARGIN = CONFIG.shadow_blur + 12


class MainLayout(QWidget):
    """Composes Header, Sidebar, Content Area, and Footer inside a rounded, shadowed frame."""

    def __init__(
        self,
        theme_manager: ThemeManager,
        navigation_items: list[NavigationItem],
        navigation_manager: NavigationManager,
        content_area: QWidget,
        group_labels: dict[str, str] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("MainLayout")

        theme = theme_manager.current_theme
        self._navigation_items = navigation_items
        self._navigation_manager = navigation_manager

        self._sidebar = Sidebar(theme, navigation_items, group_labels or get_group_labels())
        self._header = Header(theme)
        self._footer = Footer(theme)

        root = QVBoxLayout(self)
        root.setContentsMargins(_SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN)
        root.setSpacing(0)

        frame = QFrame()
        frame.setObjectName("WindowFrame")
        frame.setFrameShape(QFrame.Shape.NoFrame)
        self._shadow_effect = QGraphicsDropShadowEffect(frame)
        self._shadow_effect.setBlurRadius(CONFIG.shadow_blur)
        self._shadow_effect.setOffset(0, 3)
        self._shadow_effect.setColor(QColor(0, 0, 0, CONFIG.shadow_alpha))
        frame.setGraphicsEffect(self._shadow_effect)
        self._frame = frame

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        frame_layout.addWidget(self._header)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._sidebar)
        body.addWidget(content_area, 1)
        frame_layout.addLayout(body, 1)

        frame_layout.addWidget(self._footer)

        root.addWidget(frame)

        self._sidebar.navigation_requested.connect(navigation_manager.navigate)
        navigation_manager.current_page_changed.connect(self._sidebar.set_active_page)
        navigation_manager.current_page_changed.connect(self._on_page_changed)

        self._header.theme_toggle_requested.connect(theme_manager.toggle)
        theme_manager.theme_changed.connect(self._apply_theme)

    def _on_page_changed(self, page_id: str) -> None:
        for item in self._navigation_items:
            if item.page_id == page_id:
                self._header.set_page_title(item.label)
                return

    @property
    def header(self) -> Header:
        return self._header

    def set_window_maximized(self, maximized: bool) -> None:
        margin = 0 if maximized else _SHADOW_MARGIN
        self.layout().setContentsMargins(margin, margin, margin, margin)
        self._shadow_effect.setEnabled(not maximized)
        for widget in (self._header, self._footer):
            widget.setProperty("windowMaximized", maximized)
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _apply_theme(self, theme) -> None:
        self._header.apply_theme(theme)
        self._footer.apply_theme(theme)
        self._sidebar.apply_theme(theme)