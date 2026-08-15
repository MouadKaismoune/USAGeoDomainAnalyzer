from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon, QShowEvent
from PySide6.QtWidgets import QApplication, QStackedWidget

from config import config
from database import init_database
from translator import translator as t
from app.core.config import CONFIG
from app.ui.layouts.frameless_window import FramelessWindow
from app.ui.layouts.main_layout import MainLayout
from app.ui.navigation.navigation_config import get_group_labels, get_navigation_items
from app.ui.navigation.navigation_manager import NavigationManager
from app.ui.navigation.page_registry import PageRegistry
from app.ui.pages.home_page import HomePage
from app.ui.themes.theme import DARK, LIGHT, Theme, build_stylesheet
from app.ui.themes.theme_manager import ThemeManager


class MainWindow(FramelessWindow):
    def __init__(self, initial_theme: Theme | None = None) -> None:
        super().__init__()
        init_database()

        theme = initial_theme or (DARK if config.theme == "dark" else LIGHT)
        self._theme_manager = ThemeManager(theme, self)
        self._theme_manager.theme_changed.connect(self._apply_theme)
        self._theme_manager.theme_changed.connect(self._persist_theme)

        self.setWindowTitle(t.t("app_title"))
        self.setWindowIcon(QIcon("icon.png"))
        width = int(config.get("window_width", CONFIG.window_size[0]))
        height = int(config.get("window_height", CONFIG.window_size[1]))
        self.resize(width, height)
        self.setMinimumSize(*CONFIG.window_min_size)

        self._build_pages()
        self._register_pages()
        self._wire_analysis_signals()

        self._content_area = QStackedWidget()
        self._content_area.setObjectName("ContentArea")

        self._navigation_manager = NavigationManager(self._content_area, self._registry)

        layout = MainLayout(
            self._theme_manager,
            self._navigation_items,
            self._navigation_manager,
            self._content_area,
            get_group_labels(),
        )
        self.setCentralWidget(layout)

        self.set_drag_region(layout.header)
        self.maximized_changed.connect(self._on_maximized_changed)
        layout.header.minimize_requested.connect(self.showMinimized)
        layout.header.maximize_requested.connect(self.toggle_maximize)
        layout.header.close_requested.connect(self.close)

        self._layout = layout
        self._apply_theme(self._theme_manager.current_theme)
        self._navigation_manager.navigate("home")
        t.on_language_changed(self._on_language_changed)

    def _build_pages(self) -> None:
        from moduls.cities.ui import CitiesWidget
        from moduls.niches.ui import NichesWidget
        from moduls.analyzer.ui import AnalyzerWidget
        from moduls.domains.ui import DomainsWidget
        from moduls.maintenance.ui import MaintenanceWidget
        from moduls.backup.ui import BackupWidget
        from moduls.info.ui import InfoWidget

        self._home_page = HomePage()
        self._cities_widget = CitiesWidget()
        self._niches_widget = NichesWidget()
        self._analyzer_widget = AnalyzerWidget()
        self._domains_widget = DomainsWidget()
        self._maintenance_widget = MaintenanceWidget()
        self._backup_widget = BackupWidget()
        self._info_widget = InfoWidget()

        self._pages = {
            "home": self._home_page,
            "cities": self._cities_widget,
            "niches": self._niches_widget,
            "analyzer": self._analyzer_widget,
            "domains": self._domains_widget,
            "maintenance": self._maintenance_widget,
            "backup": self._backup_widget,
            "info": self._info_widget,
        }

    def _register_pages(self) -> None:
        self._navigation_items = get_navigation_items()
        self._registry = PageRegistry()
        for item in self._navigation_items:
            self._registry.register(item.page_id, lambda pid=item.page_id: self._pages[pid])

    def _wire_analysis_signals(self) -> None:
        self._analyzer_widget.niche_done.connect(self._on_analysis_done)
        self._maintenance_widget.done.connect(self._on_analysis_done)
        self._backup_widget.data_restored.connect(self._on_analysis_done)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if CONFIG.window_start_maximized and not self.isMaximized():
            self._maximize()

    def _on_maximized_changed(self, maximized: bool) -> None:
        self._layout.header.set_maximized(maximized)
        self._layout.set_window_maximized(maximized)

    def _apply_theme(self, theme: Theme) -> None:
        QApplication.instance().setStyleSheet(build_stylesheet(theme))
        if hasattr(self, "_home_page"):
            self._home_page.apply_theme(theme)

    def _persist_theme(self, theme: Theme) -> None:
        config.theme = theme.name

    def _on_language_changed(self, lang_code: str) -> None:
        self.setWindowTitle(t.t("app_title"))
        self._navigation_items = get_navigation_items()
        self._layout.update_navigation(self._navigation_items, get_group_labels())
        self._home_page.retranslate()
        for widget in (self._cities_widget, self._niches_widget, self._domains_widget, self._backup_widget):
            widget.refresh_data()

    def _on_analysis_done(self) -> None:
        self._cities_widget.refresh_data()
        self._niches_widget.refresh_data()
        self._domains_widget.refresh_data()
        self._home_page.refresh()

    def closeEvent(self, event: QCloseEvent) -> None:
        config.set("window_width", self.width())
        config.set("window_height", self.height())
        event.accept()