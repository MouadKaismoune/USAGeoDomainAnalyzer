from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from app.core.config import CONFIG
from app.core.icons import load_icon, load_logo_pixmap
from app.ui.themes.theme import Theme

_WINDOW_BUTTON_SIZE = 32
_BRAND_ICON_SIZE = 30


class Header(QFrame):
    theme_toggle_requested = Signal()
    minimize_requested = Signal()
    maximize_requested = Signal()
    close_requested = Signal()

    def __init__(self, theme: Theme, parent=None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._maximized = False
        self.setObjectName("Header")
        self.setFixedHeight(CONFIG.header_height)

        grid = QGridLayout(self)
        grid.setContentsMargins(20, 0, 8, 0)
        grid.setVerticalSpacing(0)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

        brand_widget = QWidget()
        brand_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        brand_layout = QHBoxLayout(brand_widget)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(10)

        brand_icon = QLabel()
        brand_icon.setObjectName("HeaderBrandIcon")
        logo = load_logo_pixmap(_BRAND_ICON_SIZE)
        if not logo.isNull():
            brand_icon.setPixmap(logo)
        brand_icon.setFixedSize(_BRAND_ICON_SIZE, _BRAND_ICON_SIZE)
        brand_layout.addWidget(brand_icon, 0, Qt.AlignmentFlag.AlignVCenter)

        brand = QLabel(CONFIG.name)
        brand.setObjectName("HeaderTitle")
        brand_layout.addWidget(brand, 0, Qt.AlignmentFlag.AlignVCenter)

        grid.addWidget(brand_widget, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        self._page_title = QLabel(CONFIG.name)
        self._page_title.setObjectName("HeaderPageTitle")
        self._page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self._page_title, 0, 1)

        right = QWidget()
        right.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        right_layout = QHBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        version = QLabel(f"v{CONFIG.version}")
        version.setObjectName("HeaderText")
        right_layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignRight)
        right_layout.addSpacing(4)

        self._theme_button = self._build_action_button("HeaderAction")
        self._theme_button.clicked.connect(self.theme_toggle_requested.emit)
        right_layout.addWidget(self._theme_button)

        right_layout.addSpacing(4)

        self._minimize_button = self._build_window_button("Minimize")
        self._minimize_button.clicked.connect(self.minimize_requested.emit)
        right_layout.addWidget(self._minimize_button)

        self._max_button = self._build_window_button("Maximize")
        self._max_button.clicked.connect(self.maximize_requested.emit)
        right_layout.addWidget(self._max_button)

        self._close_button = self._build_window_button("Close", close=True)
        self._close_button.clicked.connect(self.close_requested.emit)
        right_layout.addWidget(self._close_button)

        grid.addWidget(right, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)

        self.apply_theme(theme)

    def set_page_title(self, title: str) -> None:
        self._page_title.setText(title)

    def _build_action_button(self, object_name: str) -> QPushButton:
        button = QPushButton()
        button.setObjectName(object_name)
        button.setIconSize(QSize(18, 18))
        button.setFixedSize(_WINDOW_BUTTON_SIZE, _WINDOW_BUTTON_SIZE)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def _build_window_button(self, tooltip: str, close: bool = False) -> QPushButton:
        button = QPushButton()
        if close:
            button.setObjectName("WindowButtonClose")
        else:
            button.setObjectName("WindowButton")
        button.setIconSize(QSize(16, 16))
        button.setFixedSize(_WINDOW_BUTTON_SIZE, _WINDOW_BUTTON_SIZE)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(tooltip)
        return button

    def apply_theme(self, theme: Theme) -> None:
        self._theme = theme
        if theme.name == "light":
            icon_name, tooltip = "moon", "Switch to dark mode"
        else:
            icon_name, tooltip = "sun", "Switch to light mode"
        self._theme_button.setIcon(load_icon(icon_name, theme.sidebar_text))
        self._theme_button.setToolTip(tooltip)
        self._refresh_window_button_icons()

    def set_maximized(self, maximized: bool) -> None:
        self._maximized = maximized
        self._refresh_window_button_icons()

    def _refresh_window_button_icons(self) -> None:
        color = self._theme.sidebar_text
        self._minimize_button.setIcon(load_icon("minimize", color))
        max_icon = "restore" if self._maximized else "maximize"
        tooltip = "Restore" if self._maximized else "Maximize"
        self._max_button.setIcon(load_icon(max_icon, color))
        self._max_button.setToolTip(tooltip)
        self._close_button.setIcon(load_icon("close", "#FFFFFF"))