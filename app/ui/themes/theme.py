from __future__ import annotations

from dataclasses import dataclass, fields


@dataclass(frozen=True)
class Theme:
    name: str

    background: str
    surface: str
    border: str

    text_primary: str
    text_secondary: str

    sidebar_bg: str
    sidebar_border: str
    sidebar_hover_bg: str
    sidebar_text: str
    sidebar_text_hover: str

    primary: str
    primary_hover: str
    primary_tint: str

    success: str
    success_tint: str
    warning: str
    warning_tint: str
    error: str
    error_tint: str
    error_hover: str

    radius_small: int = 8
    radius_medium: int = 12
    font_family: str = "Segoe UI"
    font_size: int = 14


LIGHT = Theme(
    name="light",
    background="#F4F5F7",
    surface="#FFFFFF",
    border="#E2E6EC",
    text_primary="#1E2430",
    text_secondary="#5B6472",
    sidebar_bg="#FFFFFF",
    sidebar_border="#E2E6EC",
    sidebar_hover_bg="#EFF1F5",
    sidebar_text="#5B6472",
    sidebar_text_hover="#1E2430",
    primary="#3B82F6",
    primary_hover="#2E6FE0",
    primary_tint="#EAF2FE",
    success="#16A34A",
    success_tint="#E7F6EE",
    warning="#D97706",
    warning_tint="#FDF3E3",
    error="#DC2626",
    error_tint="#FDE8E8",
    error_hover="#B91C1C",
)

DARK = Theme(
    name="dark",
    background="#15171E",
    surface="#1E212B",
    border="#2B2F3A",
    text_primary="#E8EBF2",
    text_secondary="#9CA3B2",
    sidebar_bg="#0F1117",
    sidebar_border="#1B1F29",
    sidebar_hover_bg="#1C202B",
    sidebar_text="#8A93A5",
    sidebar_text_hover="#D7DCE6",
    primary="#4F8EF7",
    primary_hover="#3D7EF0",
    primary_tint="#1B2A4A",
    success="#22C55E",
    success_tint="#16301F",
    warning="#F59E0B",
    warning_tint="#33280F",
    error="#EF4444",
    error_tint="#331518",
    error_hover="#DC2626",
)

_TEMPLATE = """
QWidget {
    color: @text_primary;
    font-family: @font_family;
    font-size: @font_size;
}

#ContentArea {
    background-color: @background;
}

#MainLayout {
    background: transparent;
}

#WindowFrame {
    background: transparent;
}

#Header {
    background-color: @sidebar_bg;
    border-top-left-radius: @radius_medium;
    border-top-right-radius: @radius_medium;
}

#Header[windowMaximized="true"],
#Footer[windowMaximized="true"] {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
}

#Footer {
    background-color: @sidebar_bg;
    border-bottom-left-radius: @radius_medium;
    border-bottom-right-radius: @radius_medium;
}

#HeaderTitle,
#HeaderPageTitle {
    color: @sidebar_text_hover;
    font-size: 15px;
    font-weight: 600;
}

#HeaderBrandIcon {
    background-color: @sidebar_hover_bg;
    border-radius: 15px;
}

#HeaderText,
#FooterText {
    color: @sidebar_text;
    font-size: 12px;
}

#Sidebar {
    background-color: @sidebar_bg;
    border: none;
}

#SidebarScroll,
#NavList {
    background: transparent;
    border: none;
}

#Sidebar QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 4px 2px;
}

#Sidebar QScrollBar::handle:vertical {
    background: @sidebar_border;
    border-radius: 3px;
    min-height: 24px;
}

#Sidebar QScrollBar::handle:vertical:hover {
    background: @sidebar_text;
}

#Sidebar QScrollBar::add-line:vertical,
#Sidebar QScrollBar::sub-line:vertical {
    height: 0;
}

#ToggleButton {
    background: transparent;
    border: none;
    border-radius: @radius_small;
}

#ToggleButton:hover {
    background-color: @sidebar_hover_bg;
}

#HeaderAction {
    background: transparent;
    border: none;
    border-radius: @radius_small;
}

#HeaderAction:hover {
    background-color: @sidebar_hover_bg;
}

#FooterIcon {
    background: transparent;
    border: none;
    border-radius: 6px;
}

#FooterIcon:hover {
    background-color: @sidebar_hover_bg;
}

#FooterIcon:pressed {
    background-color: @sidebar_border;
}

#WindowButton {
    background-color: @sidebar_hover_bg;
    border: none;
    border-radius: @radius_medium;
}

#WindowButton:hover {
    background-color: @sidebar_border;
}

#WindowButtonClose {
    background-color: @error;
    border: none;
    border-radius: @radius_medium;
}

#WindowButtonClose:hover {
    background-color: @error_hover;
    color: #FFFFFF;
}

#NavGroupLabel {
    color: @sidebar_text;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 8px 10px 2px 10px;
}

#NavItem {
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-radius: @radius_small;
    text-align: left;
    padding-left: 10px;
    color: @sidebar_text;
}

#NavItem[collapsed="true"] {
    border-left-width: 0px;
    text-align: center;
    padding-left: 0;
}

#NavItem:hover {
    background-color: @sidebar_hover_bg;
    color: @sidebar_text_hover;
}

#NavItem:checked {
    background-color: @primary_tint;
    border-left-color: @primary;
    color: @primary;
}

#PageTitle {
    color: @text_primary;
    font-size: 22px;
    font-weight: 600;
}

#PageSubtitle {
    color: @text_secondary;
    font-size: 14px;
}

#Card {
    background-color: @surface;
    border: 1px solid @border;
    border-radius: @radius_medium;
}

#CardTitle {
    color: @text_primary;
    font-size: 16px;
    font-weight: 600;
}

#CardText {
    color: @text_secondary;
    font-size: 14px;
}

#page_title {
    color: @text_primary;
    font-size: 22px;
    font-weight: 700;
    padding: 4px 0;
}

#card {
    background-color: @surface;
    border: 1px solid @border;
    border-radius: @radius_medium;
    padding: 14px;
}

#stat_value {
    color: @primary;
    font-size: 28px;
    font-weight: 700;
}

#stat_label {
    color: @text_secondary;
    font-size: 12px;
}

#StatCard {
    background-color: @surface;
    border: 1px solid @border;
    border-radius: @radius_medium;
}

#StatCard:hover {
    border-color: @primary;
}

#StatBadge {
    background-color: @sidebar_hover_bg;
    border-radius: 10px;
}

#StatCard[accent="primary"] #StatBadge {
    background-color: @primary_tint;
}

#StatCard[accent="success"] #StatBadge {
    background-color: @success_tint;
}

#StatCard[accent="warning"] #StatBadge {
    background-color: @warning_tint;
}

#StatCard[accent="error"] #StatBadge {
    background-color: @error_tint;
}

#StatValue {
    color: @text_primary;
    font-size: 26px;
    font-weight: 700;
}

#StatCard[accent="primary"] #StatValue {
    color: @primary;
}

#StatCard[accent="success"] #StatValue {
    color: @success;
}

#StatCard[accent="warning"] #StatValue {
    color: @warning;
}

#StatCard[accent="error"] #StatValue {
    color: @error;
}

#StatCaption {
    color: @text_secondary;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}

#secondary_btn {
    background-color: @surface;
    border: 1px solid @border;
    border-radius: @radius_small;
    padding: 8px 20px;
    color: @text_primary;
    font-weight: 600;
}

#secondary_btn:hover {
    background-color: @sidebar_hover_bg;
}

#delete_btn {
    background-color: @error;
    border: none;
    border-radius: @radius_small;
    padding: 8px 20px;
    color: #FFFFFF;
    font-weight: 600;
}

#delete_btn:hover {
    background-color: @error_hover;
}

QPushButton {
    background-color: @primary;
    border: none;
    border-radius: @radius_small;
    padding: 8px 20px;
    color: #FFFFFF;
    font-weight: 600;
}

QPushButton:hover {
    background-color: @primary_hover;
}

QPushButton:pressed {
    padding-top: 9px;
    padding-bottom: 7px;
}

QPushButton:disabled {
    background-color: @sidebar_hover_bg;
    color: @text_secondary;
}

QCheckBox {
    spacing: 8px;
    color: @text_primary;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid @border;
    border-radius: 4px;
    background: @surface;
}

QCheckBox::indicator:checked {
    background-color: @primary;
    border-color: @primary;
}

#AnalyzerNichesCard {
    background-color: @surface;
    border: 1px solid @border;
    border-radius: @radius_medium;
}

#AnalyzerNichesTitle {
    color: @text_primary;
    font-size: 14px;
    font-weight: 600;
}

#AnalyzerNichesCount {
    color: @text_secondary;
    font-size: 12px;
}

#AnalyzerNichesScroll {
    background: transparent;
    border: none;
}

#AnalyzerNichesScroll QWidget#AnalyzerNichesContainer {
    background: transparent;
}

#AnalyzerNicheCheck {
    color: @text_primary;
    font-size: 13px;
    padding: 4px 6px;
    border-radius: @radius_small;
    spacing: 8px;
}

#AnalyzerNicheCheck:hover {
    background-color: @sidebar_hover_bg;
}

#AnalyzerNicheCheck::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid @border;
    border-radius: 4px;
    background: @surface;
}

#AnalyzerNicheCheck::indicator:hover {
    border-color: @primary;
}

#AnalyzerNicheCheck::indicator:checked {
    background-color: @primary;
    border-color: @primary;
}

#AnalyzerDelayLabel, #AnalyzerStatusLabel {
    color: @text_secondary;
    font-size: 12px;
}

#AnalyzerStatusLabel[accent="success"] {
    color: @success;
}

#AnalyzerStatusLabel[accent="error"] {
    color: @error;
}

#AnalyzerStatLabel {
    font-size: 12px;
    font-weight: bold;
}

#AnalyzerStatLabel[accent="primary"] {
    color: @primary;
}

#AnalyzerStatLabel[accent="success"] {
    color: @success;
}

#AnalyzerStatLabel[accent="warning"] {
    color: @warning;
}

#AnalyzerOutputLabel {
    color: @text_primary;
    font-size: 13px;
    font-weight: 600;
}

#AnalyzerOutput {
    background-color: @sidebar_bg;
    border: 1px solid @border;
    border-radius: @radius_small;
    color: @text_primary;
    padding: 8px;
    selection-background-color: @primary;
    selection-color: #FFFFFF;
}

QLineEdit, QComboBox {
    background-color: @surface;
    border: 1px solid @border;
    border-radius: @radius_small;
    padding: 8px 12px;
    color: @text_primary;
    selection-background-color: @primary;
    selection-color: #FFFFFF;
}

QLineEdit:focus, QComboBox:focus {
    border: 2px solid @primary;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid @text_secondary;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: @surface;
    border: 1px solid @border;
    border-radius: @radius_small;
    color: @text_primary;
    selection-background-color: @primary;
    selection-color: #FFFFFF;
}

QTableWidget {
    background-color: @surface;
    alternate-background-color: @sidebar_hover_bg;
    border: 1px solid @border;
    border-radius: @radius_small;
    gridline-color: @border;
    selection-background-color: @primary_tint;
    selection-color: @text_primary;
    padding: 4px;
}

QTableWidget::item {
    padding: 6px;
}

QHeaderView::section {
    background-color: @sidebar_hover_bg;
    color: @text_primary;
    border: none;
    border-bottom: 2px solid @border;
    padding: 8px;
    font-weight: 600;
}

QProgressBar {
    border: 1px solid @border;
    border-radius: @radius_small;
    text-align: center;
    background-color: @sidebar_hover_bg;
    color: @text_primary;
    height: 20px;
}

QProgressBar::chunk {
    background-color: @primary;
    border-radius: 6px;
}

QTextEdit {
    background-color: @surface;
    border: 1px solid @border;
    border-radius: @radius_small;
    color: @text_primary;
    padding: 8px;
    selection-background-color: @primary;
    selection-color: #FFFFFF;
}

QTabWidget::pane {
    border: 1px solid @border;
    border-radius: @radius_medium;
    background-color: @surface;
}

QTabBar::tab {
    background: transparent;
    color: @text_secondary;
    padding: 8px 18px;
    border-bottom: 2px solid transparent;
    font-weight: 600;
}

QTabBar::tab:selected {
    color: @primary;
    border-bottom: 2px solid @primary;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px 2px;
}

QScrollBar::handle:vertical {
    background: @border;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: @text_secondary;
}

QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px 4px;
}

QScrollBar::handle:horizontal {
    background: @border;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: @text_secondary;
}

QScrollBar::add-line, QScrollBar::sub-line {
    width: 0;
    height: 0;
}

QMessageBox {
    background-color: @surface;
}
"""


def build_stylesheet(theme: Theme) -> str:
    qss = _TEMPLATE
    for field in sorted(fields(theme), key=lambda f: len(f.name), reverse=True):
        qss = qss.replace(f"@{field.name}", str(getattr(theme, field.name)))
    return qss
