from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from app.core.config import ASSETS_DIR


def load_icon(name: str, color: str, size: int = 24) -> QIcon:
    """Load an SVG icon from assets, tinted with the given color."""
    return QIcon(load_icon_pixmap(name, color, size))


def load_icon_pixmap(name: str, color: str, size: int = 24) -> QPixmap:
    """Load an SVG icon from assets as a tinted pixmap."""
    path = ASSETS_DIR / "icons" / f"{name}.svg"
    svg = path.read_text(encoding="utf-8").replace("currentColor", color)
    renderer = QSvgRenderer(svg.encode("utf-8"))
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap
