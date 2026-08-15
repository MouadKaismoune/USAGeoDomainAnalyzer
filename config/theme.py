from PySide6.QtGui import QColor

LIGHT_THEME = {
    "name": "light",
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F5F5F5",
    "bg_sidebar": "#2C3E50",
    "bg_card": "#FFFFFF",
    "bg_hover": "#E8E8E8",
    "bg_input": "#F0F0F0",
    "text_primary": "#2C3E50",
    "text_secondary": "#7F8C8D",
    "text_sidebar": "#ECF0F1",
    "text_sidebar_hover": "#FFFFFF",
    "accent": "#3498DB",
    "accent_hover": "#2980B9",
    "success": "#27AE60",
    "danger": "#E74C3C",
    "warning": "#F39C12",
    "border": "#E0E0E0",
    "table_header": "#F8F9FA",
    "table_row_alt": "#FAFAFA",
    "shadow": "#00000020",
}

DARK_THEME = {
    "name": "dark",
    "bg_primary": "#1E1E2E",
    "bg_secondary": "#282840",
    "bg_sidebar": "#181825",
    "bg_card": "#282840",
    "bg_hover": "#383855",
    "bg_input": "#313145",
    "text_primary": "#CDD6F4",
    "text_secondary": "#A6ADC8",
    "text_sidebar": "#CDD6F4",
    "text_sidebar_hover": "#FFFFFF",
    "accent": "#89B4FA",
    "accent_hover": "#74C7EC",
    "success": "#A6E3A1",
    "danger": "#F38BA8",
    "warning": "#F9E2AF",
    "border": "#45475A",
    "table_header": "#313145",
    "table_row_alt": "#242438",
    "shadow": "#00000040",
}

THEMES = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
}


def get_theme(name: str = "light") -> dict:
    return THEMES.get(name, LIGHT_THEME)


def apply_theme(app, theme_name: str = "light"):
    theme = get_theme(theme_name)
    app.setStyleSheet(f"""
        QWidget {{
            background-color: {theme['bg_primary']};
            color: {theme['text_primary']};
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 13px;
        }}

        QFrame#sidebar {{
            background-color: {theme['bg_sidebar']};
        }}

        QPushButton#sidebar_btn {{
            background-color: transparent;
            color: {theme['text_sidebar']};
            border: none;
            text-align: left;
            padding: 12px 20px;
            font-size: 14px;
            border-radius: 6px;
            margin: 2px 8px;
        }}

        QPushButton#sidebar_btn:hover {{
            background-color: {theme['bg_hover']};
            color: {theme['text_sidebar_hover']};
        }}

        QPushButton#sidebar_btn[active="true"] {{
            background-color: {theme['accent']};
            color: {theme['text_sidebar_hover']};
        }}

        QLabel#sidebar_title {{
            color: {theme['text_sidebar']};
            font-size: 16px;
            font-weight: bold;
            padding: 16px 20px;
        }}

        QFrame#content_area {{
            background-color: {theme['bg_primary']};
        }}

        QFrame#card {{
            background-color: {theme['bg_card']};
            border: 1px solid {theme['border']};
            border-radius: 10px;
            padding: 16px;
        }}

        QLineEdit {{
            background-color: {theme['bg_input']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 8px 12px;
            color: {theme['text_primary']};
            font-size: 13px;
        }}

        QLineEdit:focus {{
            border: 2px solid {theme['accent']};
        }}

        QPushButton {{
            background-color: {theme['accent']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 20px;
            font-size: 13px;
            font-weight: bold;
        }}

        QPushButton:hover {{
            background-color: {theme['accent_hover']};
        }}

        QPushButton:pressed {{
            padding-top: 2px;
        }}

        QPushButton#delete_btn {{
            background-color: {theme['danger']};
        }}

        QPushButton#delete_btn:hover {{
            background-color: #C0392B;
        }}

        QPushButton#secondary_btn {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
        }}

        QTableWidget {{
            background-color: {theme['bg_card']};
            alternate-background-color: {theme['table_row_alt']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
            gridline-color: {theme['border']};
            selection-background-color: {theme['accent']};
            selection-color: white;
        }}

        QTableWidget::item {{
            padding: 8px;
        }}

        QHeaderView::section {{
            background-color: {theme['table_header']};
            color: {theme['text_primary']};
            border: none;
            border-bottom: 2px solid {theme['border']};
            padding: 10px 8px;
            font-weight: bold;
            font-size: 13px;
        }}

        QComboBox {{
            background-color: {theme['bg_input']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 8px 12px;
            color: {theme['text_primary']};
            min-width: 120px;
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {theme['bg_card']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            selection-background-color: {theme['accent']};
        }}

        QProgressBar {{
            border: 1px solid {theme['border']};
            border-radius: 6px;
            text-align: center;
            background-color: {theme['bg_input']};
            height: 20px;
        }}

        QProgressBar::chunk {{
            background-color: {theme['accent']};
            border-radius: 5px;
        }}

        QScrollBar:vertical {{
            background-color: {theme['bg_secondary']};
            width: 10px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {theme['border']};
            border-radius: 5px;
            min-height: 30px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {theme['text_secondary']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QLabel#stat_value {{
            font-size: 28px;
            font-weight: bold;
            color: {theme['accent']};
        }}

        QLabel#stat_label {{
            font-size: 12px;
            color: {theme['text_secondary']};
        }}

        QLabel#page_title {{
            font-size: 22px;
            font-weight: bold;
            color: {theme['text_primary']};
            padding: 4px 0;
        }}
    """)
