from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtGui import QCloseEvent, QIcon, QShowEvent
from PySide6.QtWidgets import QApplication, QStackedWidget, QWidget

from config import config
from database import init_database
from translator import translator as t
from app.core.config import ASSETS_DIR, CONFIG
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
        self.setWindowIcon(QIcon(str(ASSETS_DIR.parent / "icon.png")))
        width = int(config.get("window_width", CONFIG.window_size[0]))
        height = int(config.get("window_height", CONFIG.window_size[1]))
        self.resize(width, height)
        self.setMinimumSize(*CONFIG.window_min_size)

        self._build_pages()
        self._register_pages()

        # Analysis reports progress once per niche; coalesce the follow-up
        # refreshes so tables are not rebuilt on every event.
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(400)
        self._refresh_timer.timeout.connect(self._refresh_pages)

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

    def _build_pages(self) -> None:
        # Pages are created lazily on first navigation; only the landing page
        # (Home) is built eagerly. Each page loads its data on first display,
        # so startup no longer queries the database for every module.
        self._page_widgets: dict[str, QWidget] = {}
        self._page_factories = {
            "home": self._create_home_page,
            "cities": self._create_cities_page,
            "niches": self._create_niches_page,
            "analyzer": self._create_analyzer_page,
            "domains": self._create_domains_page,
            "maintenance": self._create_maintenance_page,
            "backup": self._create_backup_page,
            "info": self._create_info_page,
        }
        self._get_page("home")

    def _get_page(self, page_id: str) -> QWidget:
        widget = self._page_widgets.get(page_id)
        if widget is None:
            widget = self._page_factories[page_id]()
            self._page_widgets[page_id] = widget
        return widget

    def _create_home_page(self) -> QWidget:
        return HomePage()

    def _create_cities_page(self) -> QWidget:
        from moduls.cities.ui import CitiesWidget
        return CitiesWidget()

    def _create_niches_page(self) -> QWidget:
        from moduls.niches.ui import NichesWidget
        return NichesWidget()

    def _create_analyzer_page(self) -> QWidget:
        from moduls.analyzer.ui import AnalyzerWidget
        widget = AnalyzerWidget()
        widget.niche_done.connect(self._on_analysis_done)
        return widget

    def _create_domains_page(self) -> QWidget:
        from moduls.domains.ui import DomainsWidget
        return DomainsWidget()

    def _create_maintenance_page(self) -> QWidget:
        from moduls.maintenance.ui import MaintenanceWidget
        widget = MaintenanceWidget()
        widget.done.connect(self._on_analysis_done)
        return widget

    def _create_backup_page(self) -> QWidget:
        from moduls.backup.ui import BackupWidget
        widget = BackupWidget()
        widget.data_restored.connect(self._on_analysis_done)
        return widget

    def _create_info_page(self) -> QWidget:
        from moduls.info.ui import InfoWidget
        return InfoWidget()

    def _register_pages(self) -> None:
        self._navigation_items = get_navigation_items()
        self._registry = PageRegistry()
        for item in self._navigation_items:
            self._registry.register(item.page_id, lambda pid=item.page_id: self._get_page(pid))

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if CONFIG.window_start_maximized and not self.isMaximized():
            self._maximize()

    def _on_maximized_changed(self, maximized: bool) -> None:
        self._layout.header.set_maximized(maximized)
        self._layout.set_window_maximized(maximized)

    def _apply_theme(self, theme: Theme) -> None:
        QApplication.instance().setStyleSheet(build_stylesheet(theme))
        home = self._page_widgets.get("home")
        if home is not None:
            home.apply_theme(theme)

    def _persist_theme(self, theme: Theme) -> None:
        config.theme = theme.name

    def _on_analysis_done(self) -> None:
        # Coalesce bursts (analyser emits once per niche) into a single refresh.
        self._refresh_timer.start()

    def _refresh_pages(self) -> None:
        # Only refresh pages that have been created; never build a page just to
        # update it.
        for page_id in ("cities", "niches", "domains"):
            widget = self._page_widgets.get(page_id)
            refresh = getattr(widget, "refresh_data", None)
            if callable(refresh):
                refresh()

        home = self._page_widgets.get("home")
        if home is not None:
            home.refresh()

    def closeEvent(self, event: QCloseEvent) -> None:
        config.set("window_width", self.width())
        config.set("window_height", self.height())

        self._stop_worker_threads()

        event.accept()

    def _stop_worker_threads(self) -> None:
        """Stop any running background QThread before the window is destroyed.

        Without this, the threads are destroyed while still running, which
        triggers "QThread: Destroyed while thread is still running" and can
        abort the process.
        """
        widgets = self._page_widgets.values()
        for widget in widgets:
            thread = getattr(widget, "_thread", None)
            if thread is None or not thread.isRunning():
                continue

            # Drop queued progress/finished signals so closing UI code is not
            # invoked (e.g. modal dialogs) while the window is shutting down.
            thread.blockSignals(True)

            stop = getattr(thread, "stop", None)
            if callable(stop):
                stop()

            if not thread.wait(5000):
                thread.terminate()
                thread.wait()