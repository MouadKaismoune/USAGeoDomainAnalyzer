from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableView, QLabel, QFrame,
    QHeaderView, QComboBox, QTabWidget, QLineEdit, QAbstractItemView
)
from translator import translator as t
from moduls.domains.rdap import classify_status
from moduls.domains.table_model import (
    DomainTableModel, all_domain_columns, strength_columns,
)
from moduls.strength.controller import get_strength_results, get_domains_view


class DomainsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_domains = []
        self._all_strength = []
        self._setup_ui()

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

        self.all_table = QTableView()
        self.all_model = DomainTableModel(all_domain_columns())
        self.all_table.setModel(self.all_model)
        self.all_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.all_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.all_table.setAlternatingRowColors(True)
        self.all_table.verticalHeader().setVisible(False)
        self.all_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.all_table.setSortingEnabled(True)
        self.all_table.setWordWrap(False)
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

        self.strength_table = QTableView()
        self.strength_model = DomainTableModel(strength_columns())
        self.strength_table.setModel(self.strength_model)
        self.strength_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.strength_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.strength_table.setAlternatingRowColors(True)
        self.strength_table.verticalHeader().setVisible(False)
        self.strength_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.strength_table.setSortingEnabled(True)
        self.strength_table.setWordWrap(False)
        tab_layout.addWidget(self.strength_table, 1)

        self.tabs.addTab(strength_tab, t.t("sidebar_strength"))

    def refresh_data(self):
        # One strength computation feeds both the full table and the strength
        # tab (previously each ran its own computation).
        self._all_domains, self._all_strength = get_domains_view()
        self._apply_filters()
        self._filter_strength(self._all_strength)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()

    def _apply_filters(self):
        filters = ["All", "Available", "Registered", "Unknown"]
        status_filter = filters[self.filter_combo.currentIndex()]
        query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""

        filtered = self._all_domains
        if status_filter != "All":
            filtered = [d for d in filtered
                        if classify_status(d.get("status", "")) == status_filter.lower()]
        if query:
            filtered = [d for d in filtered if query in d.get("domain", "").lower()
                        or query in d.get("city", "").lower()
                        or query in d.get("niche", "").lower()]
        self._populate_all_table(filtered)

    def _populate_all_table(self, domains):
        self.all_count_label.setText(f"{len(domains)} domains")
        self.all_model.set_rows(domains)

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
        self.strength_count_label.setText(f"{len(results)} available domains")
        self.strength_model.set_rows(results)
