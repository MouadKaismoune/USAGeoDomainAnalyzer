from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QFrame,
    QHeaderView, QComboBox, QTabWidget, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from translator import translator as t
from moduls.domains.controller import get_domains_table_data
from moduls.strength.controller import get_strength_results
from widgets import NumericTableWidgetItem, StatusTableWidgetItem, DateTableWidgetItem


class DomainsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_domains = []
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel(t.t("domains_title"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._setup_all_tab()
        self._setup_strength_tab()

    def _setup_all_tab(self):
        all_tab = QWidget()
        tab_layout = QVBoxLayout(all_tab)
        tab_layout.setContentsMargins(12, 8, 12, 8)
        tab_layout.setSpacing(10)

        filter_frame = QFrame()
        filter_frame.setObjectName("card")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(12)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            t.t("domains_filter_all"),
            t.t("domains_filter_available"),
            t.t("domains_filter_registered"),
            t.t("domains_filter_unknown"),
        ])
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(QLabel(t.t("common_search") + ":"))
        filter_layout.addWidget(self.filter_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t.t("common_search"))
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search)
        filter_layout.addWidget(self.search_input)

        filter_layout.addStretch()

        self.all_count_label = QLabel("")
        self.all_count_label.setStyleSheet("color: #7F8C8D; font-size: 12px;")
        filter_layout.addWidget(self.all_count_label)

        tab_layout.addWidget(filter_frame)

        self.all_table = QTableWidget()
        self.all_table.setColumnCount(9)
        self.all_table.setHorizontalHeaderLabels([
            "#", "Domain", "Status", "City", "Niche", "Date",
            "City Str%", "Niche Str%", "Strength"
        ])
        self.all_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.all_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.all_table.setAlternatingRowColors(True)
        self.all_table.verticalHeader().setVisible(False)
        self.all_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.all_table.setSortingEnabled(True)
        tab_layout.addWidget(self.all_table, 1)

        self.tabs.addTab(all_tab, t.t("domains_filter_all"))

    def _setup_strength_tab(self):
        strength_tab = QWidget()
        tab_layout = QVBoxLayout(strength_tab)
        tab_layout.setContentsMargins(12, 8, 12, 8)
        tab_layout.setSpacing(10)

        top_frame = QFrame()
        top_frame.setObjectName("card")
        top_layout = QHBoxLayout(top_frame)

        self.calc_btn = QPushButton(t.t("strength_calculate"))
        self.calc_btn.clicked.connect(self._load_strength)
        top_layout.addWidget(self.calc_btn)

        self.strength_search = QLineEdit()
        self.strength_search.setPlaceholderText(t.t("common_search"))
        self.strength_search.setClearButtonEnabled(True)
        self.strength_search.textChanged.connect(self._on_strength_search)
        top_layout.addWidget(self.strength_search)

        top_layout.addStretch()

        self.strength_count_label = QLabel("")
        self.strength_count_label.setStyleSheet("color: #7F8C8D; font-size: 12px;")
        top_layout.addWidget(self.strength_count_label)
        tab_layout.addWidget(top_frame)

        self.strength_table = QTableWidget()
        self.strength_table.setColumnCount(7)
        self.strength_table.setHorizontalHeaderLabels([
            "#", "Domain", "City", "Niche", "City%", "Niche%", "Score"
        ])
        self.strength_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.strength_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.strength_table.setAlternatingRowColors(True)
        self.strength_table.verticalHeader().setVisible(False)
        self.strength_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.strength_table.setSortingEnabled(True)
        tab_layout.addWidget(self.strength_table, 1)

        self.tabs.addTab(strength_tab, t.t("sidebar_strength"))

    def refresh_data(self):
        self._all_domains = get_domains_table_data("All")
        self._apply_filters()
        self._load_strength()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()

    def _apply_filters(self):
        filters = ["All", "Available", "Registered", "Unknown"]
        status_filter = filters[self.filter_combo.currentIndex()]
        query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""

        filtered = self._all_domains
        if status_filter != "All":
            filtered = [d for d in filtered if d.get("status", "").lower() == status_filter.lower()]
        if query:
            filtered = [d for d in filtered if query in d.get("domain", "").lower()
                        or query in d.get("city", "").lower()
                        or query in d.get("niche", "").lower()]
        self._populate_all_table(filtered)

    def _populate_all_table(self, domains):
        self.all_table.setSortingEnabled(False)
        self.all_count_label.setText(f"{len(domains)} domains")
        self.all_table.setRowCount(len(domains))
        for i, d in enumerate(domains):
            num_item = NumericTableWidgetItem(str(i + 1), i + 1)
            num_item.setTextAlignment(Qt.AlignCenter)
            self.all_table.setItem(i, 0, num_item)
            self.all_table.setItem(i, 1, QTableWidgetItem(d.get("domain", "")))

            status = d.get("status", "")
            status_item = StatusTableWidgetItem(status)
            if "available" in status.lower() and "registered" not in status.lower():
                status_item.setForeground(QColor("#27AE60"))
            elif "registered" in status.lower():
                status_item.setForeground(QColor("#E74C3C"))
            else:
                status_item.setForeground(QColor("#F39C12"))
            self.all_table.setItem(i, 2, status_item)

            self.all_table.setItem(i, 3, QTableWidgetItem(d.get("city", "")))
            self.all_table.setItem(i, 4, QTableWidgetItem(d.get("niche", "")))
            date_item = DateTableWidgetItem(d.get("date", "") or "")
            date_item.setTextAlignment(Qt.AlignCenter)
            self.all_table.setItem(i, 5, date_item)

            city_str = d.get('city_strength', 0)
            cs = NumericTableWidgetItem(f"{city_str:.1f}", city_str)
            cs.setTextAlignment(Qt.AlignCenter)
            self.all_table.setItem(i, 6, cs)

            niche_str = d.get('niche_strength', 0)
            ns = NumericTableWidgetItem(f"{niche_str:.1f}", niche_str)
            ns.setTextAlignment(Qt.AlignCenter)
            self.all_table.setItem(i, 7, ns)

            str_val = d.get("strength", 0)
            strength_item = NumericTableWidgetItem(f"{str_val:.1f}", str_val)
            strength_item.setTextAlignment(Qt.AlignCenter)
            if str_val >= 50:
                strength_item.setForeground(QColor("#E74C3C"))
            elif str_val >= 25:
                strength_item.setForeground(QColor("#F39C12"))
            else:
                strength_item.setForeground(QColor("#27AE60"))
            self.all_table.setItem(i, 8, strength_item)

        self.all_table.setSortingEnabled(True)

    def _on_filter_changed(self, index):
        self._apply_filters()

    def _on_search(self, text):
        self._apply_filters()

    def _load_strength(self):
        self._all_strength = get_strength_results()
        self._filter_strength(self._all_strength)

    def _on_strength_search(self, text):
        query = text.strip().lower()
        if not query:
            self._filter_strength(self._all_strength)
            return
        filtered = [r for r in self._all_strength if query in r["domain"].lower()
                    or query in r["city"].lower()
                    or query in r["niche"].lower()]
        self._filter_strength(filtered)

    def _filter_strength(self, results):
        self.strength_table.setSortingEnabled(False)
        self.strength_count_label.setText(f"{len(results)} available domains")
        self.strength_table.setRowCount(len(results))
        for i, r in enumerate(results):
            num_item = NumericTableWidgetItem(str(i + 1), i + 1)
            num_item.setTextAlignment(Qt.AlignCenter)
            self.strength_table.setItem(i, 0, num_item)
            self.strength_table.setItem(i, 1, QTableWidgetItem(r["domain"]))
            self.strength_table.setItem(i, 2, QTableWidgetItem(r["city"]))
            self.strength_table.setItem(i, 3, QTableWidgetItem(r["niche"]))

            city_pct_val = r["city_registered_pct"]
            city_pct = NumericTableWidgetItem(str(city_pct_val), city_pct_val)
            city_pct.setTextAlignment(Qt.AlignCenter)
            self.strength_table.setItem(i, 4, city_pct)

            niche_pct_val = r["niche_registered_pct"]
            niche_pct = NumericTableWidgetItem(str(niche_pct_val), niche_pct_val)
            niche_pct.setTextAlignment(Qt.AlignCenter)
            self.strength_table.setItem(i, 5, niche_pct)

            score_val = r["total_score"]
            score = NumericTableWidgetItem(str(score_val), score_val)
            score.setTextAlignment(Qt.AlignCenter)
            if score_val >= 50:
                score.setForeground(QColor("#27AE60"))
            elif score_val >= 25:
                score.setForeground(QColor("#F39C12"))
            else:
                score.setForeground(QColor("#E74C3C"))
            self.strength_table.setItem(i, 6, score)

        self.strength_table.setSortingEnabled(True)
