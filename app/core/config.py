from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"


@dataclass(frozen=True)
class AppConfig:
    name: str = "USAGeoDomainAnalyzer"
    version: str = "26.10"
    developer: str = "Kaismoune Mouad"
    developer_location: str = "Algeria"
    linkedin_url: str = "https://www.linkedin.com/in/mouadkaismoune/"
    github_url: str = "https://github.com/MouadKaismoune/USAGeoDomainAnalyzer"
    email_address: str = "kaismounemouad@gmail.com"
    window_title: str = "USAGeoDomainAnalyzer"
    window_size: tuple[int, int] = (1440, 860)
    window_min_size: tuple[int, int] = (1000, 640)
    window_start_maximized: bool = True
    window_radius: int = 12
    resize_margin: int = 6
    shadow_blur: int = 42
    shadow_alpha: int = 160
    sidebar_expanded_width: int = 224
    sidebar_collapsed_width: int = 64
    sidebar_animation_duration: int = 180
    header_height: int = 56
    footer_height: int = 36


CONFIG = AppConfig()