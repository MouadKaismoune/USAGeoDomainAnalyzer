import webbrowser

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QSizePolicy,
)

from translator import translator as t
from app.core.config import CONFIG
from app.core.contact import contact_links
from app.core.icons import load_icon, load_logo_pixmap

_CONTACT_BUTTONS = (
    ("linkedin", "info_linkedin", "linkedin"),
    ("github", "info_github", "github"),
    ("email", "info_email", "email"),
)


def _accent_color() -> str:
    from config import config
    from app.ui.themes.theme import DARK, LIGHT
    return (DARK if config.theme == "dark" else LIGHT).primary


class InfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel(t.t("info_title"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        about_card = QFrame()
        about_card.setObjectName("card")
        about_layout = QVBoxLayout(about_card)
        about_layout.setSpacing(10)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(14)

        icon_label = QLabel()
        icon_label.setPixmap(load_logo_pixmap(56))
        icon_label.setFixedSize(56, 56)
        brand_row.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignVCenter)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(2)
        self.name_label = QLabel(CONFIG.name)
        self.name_label.setObjectName("AnalyzerNichesTitle")
        self.name_label.setStyleSheet("font-size: 18px; font-weight: 700;")
        brand_text.addWidget(self.name_label)
        self.version_label = QLabel(t.t("info_version", version=CONFIG.version))
        self.version_label.setObjectName("AnalyzerNichesCount")
        brand_text.addWidget(self.version_label)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()
        about_layout.addLayout(brand_row)

        self.about_label = QLabel(t.t("info_description"))
        self.about_label.setWordWrap(True)
        self.about_label.setObjectName("CardText")
        about_layout.addWidget(self.about_label)

        layout.addWidget(about_card)

        dev_card = QFrame()
        dev_card.setObjectName("card")
        dev_layout = QHBoxLayout(dev_card)
        dev_layout.setSpacing(16)

        dev_title = QVBoxLayout()
        dev_title.setSpacing(2)
        dev_caption = QLabel(t.t("info_developer"))
        dev_caption.setObjectName("AnalyzerNichesCount")
        dev_title.addWidget(dev_caption)
        self.developer_label = QLabel(CONFIG.developer)
        self.developer_label.setObjectName("AnalyzerNichesTitle")
        self.developer_label.setStyleSheet("font-size: 16px; font-weight: 700;")
        dev_title.addWidget(self.developer_label)
        dev_layout.addLayout(dev_title)

        dev_layout.addStretch()

        self.location_label = QLabel(CONFIG.developer_location)
        self.location_label.setObjectName("AnalyzerNichesCount")
        dev_layout.addWidget(self.location_label, 0, Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(dev_card)

        contact_card = QFrame()
        contact_card.setObjectName("card")
        contact_layout = QVBoxLayout(contact_card)
        contact_layout.setSpacing(10)

        self.contact_title = QLabel(t.t("info_contact"))
        self.contact_title.setObjectName("AnalyzerNichesTitle")
        self.contact_title.setStyleSheet("font-size: 16px; font-weight: 700;")
        contact_layout.addWidget(self.contact_title)

        self.contact_subtitle = QLabel(t.t("info_contact_subtitle"))
        self.contact_subtitle.setWordWrap(True)
        self.contact_subtitle.setObjectName("CardText")
        contact_layout.addWidget(self.contact_subtitle)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)
        self._contact_buttons = {}
        for icon, key, tid in _CONTACT_BUTTONS:
            button = QPushButton(t.t(key))
            button.setObjectName("secondary_btn")
            button.setIcon(load_icon(icon, _accent_color()))
            button.setIconSize(QSize(18, 18))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(lambda _=False, name=tid: self._open_contact(name))
            buttons_row.addWidget(button)
            self._contact_buttons[tid] = button
        contact_layout.addLayout(buttons_row)

        layout.addWidget(contact_card)

        layout.addStretch(1)

    def _open_contact(self, name: str) -> None:
        url = contact_links().get(name)
        if url:
            webbrowser.open(url)