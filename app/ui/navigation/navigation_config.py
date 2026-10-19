from __future__ import annotations

from dataclasses import dataclass

from translator import translator as t


@dataclass(frozen=True)
class NavigationItem:
    page_id: str
    label: str
    icon: str
    group: str | None = None


def get_navigation_items() -> list[NavigationItem]:
    return [
        NavigationItem(page_id="home", label=t.t("sidebar_home"), icon="home", group="Main"),
        NavigationItem(page_id="cities", label=t.t("sidebar_cities"), icon="cities", group="Main"),
        NavigationItem(page_id="niches", label=t.t("sidebar_niches"), icon="niches", group="Main"),
        NavigationItem(page_id="analyzer", label=t.t("sidebar_analyzer"), icon="analyzer", group="Analysis"),
        NavigationItem(page_id="domains", label=t.t("sidebar_domains"), icon="domains", group="Analysis"),
        NavigationItem(page_id="maintenance", label=t.t("sidebar_maintenance"), icon="maintenance", group="System"),
        NavigationItem(page_id="backup", label=t.t("sidebar_backup"), icon="backup", group="System"),
        NavigationItem(page_id="info", label=t.t("sidebar_info"), icon="info", group="System"),
    ]


def get_group_labels() -> dict[str, str]:
    return {
        "Main": t.t("nav_group_main"),
        "Analysis": t.t("nav_group_analysis"),
        "System": t.t("nav_group_system"),
    }