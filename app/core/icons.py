from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPainterPath, QPixmap
from PySide6.QtSvg import QSvgRenderer

from app.core.config import ASSETS_DIR, PROJECT_ROOT

LOGO_PATH = PROJECT_ROOT / "icon.png"


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


def load_logo_pixmap(size: int) -> QPixmap:
    """Load the app logo (``icon.png``) cropped into a circular pixmap."""
    source = QPixmap(str(LOGO_PATH))
    rounded = QPixmap(size, size)
    rounded.fill(Qt.GlobalColor.transparent)
    if source.isNull():
        return rounded

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    clip = QPainterPath()
    clip.addRoundedRect(0, 0, size, size, size / 2, size / 2)
    painter.setClipPath(clip)
    painter.drawPixmap(0, 0, size, size, source)
    painter.end()
    return rounded
