from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from config import config
from app.core.config import CONFIG
from app.ui.layouts.main_window import MainWindow
from app.ui.themes.theme import DARK, LIGHT


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(CONFIG.name)
    app.setStyle("Fusion")

    initial_theme = DARK if config.theme == "dark" else LIGHT
    window = MainWindow(initial_theme=initial_theme)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()