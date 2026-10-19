from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QSize, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
)

from app.core.config import CONFIG
from app.core.icons import load_icon
from app.ui.navigation.navigation_config import NavigationItem, get_group_labels
from app.ui.themes.theme import Theme


def _active_color(checked: bool, theme: Theme) -> str:
    return theme.primary if checked else theme.sidebar_text


class Sidebar(QFrame):
    navigation_requested = Signal(str)

    def __init__(
        self,
        theme: Theme,
        navigation_items: list[NavigationItem],
        group_labels: dict[str, str] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._expanded = True
        self._buttons: dict[str, QToolButton] = {}
        self._labels: dict[str, str] = {}
        self._icon_names: dict[str, str] = {}
        self._animation: QPropertyAnimation | None = None

        self.setObjectName("Sidebar")
        self.setMinimumWidth(CONFIG.sidebar_expanded_width)
        self.setMaximumWidth(CONFIG.sidebar_expanded_width)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 12, 10, 10)
        root.setSpacing(4)

        self._toggle_button = QPushButton()
        self._toggle_button.setObjectName("ToggleButton")
        self._toggle_button.setIcon(load_icon("menu", self._theme.sidebar_text))
        self._toggle_button.setIconSize(QSize(20, 20))
        self._toggle_button.setFixedHeight(40)
        self._toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_button.setToolTip("Toggle sidebar")
        self._toggle_button.clicked.connect(self.toggle)
        root.addWidget(self._toggle_button)

        scroll = QScrollArea()
        scroll.setObjectName("SidebarScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        container = QFrame()
        container.setObjectName("NavList")
        container.setFrameShape(QFrame.Shape.NoFrame)
        self._nav_layout = QVBoxLayout(container)
        self._nav_layout.setContentsMargins(0, 4, 0, 4)
        self._nav_layout.setSpacing(4)
        self._nav_layout.addStretch(1)

        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        self._group_labels: dict[str, QLabel] = {}
        self._label_mapping = group_labels or get_group_labels()
        last_group = None
        for item in navigation_items:
            if item.group != last_group:
                last_group = item.group
                if item.group:
                    self._add_group_label(item.group)
            self._add_nav_item(item)

    def _add_group_label(self, group: str) -> None:
        text = self._label_mapping.get(group, group.upper())
        label = QLabel(text.upper())
        label.setObjectName("NavGroupLabel")
        label.setProperty("collapsed", False)
        self._nav_layout.insertWidget(self._nav_layout.count() - 1, label)
        self._group_labels[group] = label

    def _add_nav_item(self, item: NavigationItem) -> None:
        button = QToolButton()
        button.setText(item.label)
        button.setObjectName("NavItem")
        button.setCheckable(True)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        button.setIcon(load_icon(item.icon, self._theme.sidebar_text))
        button.setIconSize(QSize(20, 20))
        button.setFixedHeight(40)
        button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(lambda _=False, pid=item.page_id: self._on_item_clicked(pid))
        self._nav_layout.insertWidget(self._nav_layout.count() - 1, button)
        self._buttons[item.page_id] = button
        self._labels[item.page_id] = item.label
        self._icon_names[item.page_id] = item.icon

    def set_active_page(self, page_id: str) -> None:
        for pid, button in self._buttons.items():
            checked = pid == page_id
            button.setChecked(checked)
            color = _active_color(checked, self._theme)
            button.setIcon(load_icon(self._icon_names[pid], color))

    def apply_theme(self, theme: Theme) -> None:
        self._theme = theme
        self._toggle_button.setIcon(load_icon("menu", theme.sidebar_text))
        for pid, button in self._buttons.items():
            color = _active_color(button.isChecked(), theme)
            button.setIcon(load_icon(self._icon_names[pid], color))

    def _on_item_clicked(self, page_id: str) -> None:
        self.set_active_page(page_id)
        self.navigation_requested.emit(page_id)

    def toggle(self) -> None:
        self.set_expanded(not self._expanded)

    def set_expanded(self, expanded: bool) -> None:
        if expanded == self._expanded:
            return
        self._expanded = expanded
        target = (
            CONFIG.sidebar_expanded_width
            if expanded
            else CONFIG.sidebar_collapsed_width
        )
        self._start_width_animation(target)

    def _start_width_animation(self, target: int) -> None:
        self.setMaximumWidth(target)
        self._animation = QPropertyAnimation(self, b"minimumWidth", self)
        self._animation.setDuration(CONFIG.sidebar_animation_duration)
        self._animation.setStartValue(self.width())
        self._animation.setEndValue(target)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.finished.connect(self._on_animation_finished)
        self._animation.start()

    def _on_animation_finished(self) -> None:
        collapsed = not self._expanded
        for label in self._group_labels.values():
            label.setVisible(self._expanded)
            label.setProperty("collapsed", collapsed)
            label.style().unpolish(label)
            label.style().polish(label)
        for pid, button in self._buttons.items():
            button.setText(self._labels[pid] if self._expanded else "")
            button.setToolTip(None if self._expanded else self._labels[pid])
            self._set_button_style(button)
            button.setProperty("collapsed", collapsed)
            button.style().unpolish(button)
            button.style().polish(button)

    def _set_button_style(self, button: QToolButton) -> None:
        style = (
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            if self._expanded
            else Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        button.setToolButtonStyle(style)
