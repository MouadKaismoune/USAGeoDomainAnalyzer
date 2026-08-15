from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel,
    QFrame, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QColor
from translator import translator as t
from moduls.cities.controller import get_cities_table_data, handle_delete_city, handle_set_city_ignore
from widgets import NumericTableWidgetItem


class AddCityThread(QThread):
    progress = Signal(dict)
    finished = Signal(bool, str)

    def __init__(self, city_name, parent=None):
        super().__init__(parent)
        self._city_name = city_name

    def run(self):
        from moduls.cities.services import add_city
        success, msg = add_city(self._city_name, progress_callback=self._on_progress)
        self.finished.emit(success, msg)

    def _on_progress(self, **kwargs):
        self.progress.emit(kwargs)


class CitiesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_cities = []
        self._thread = None
        self._loading = False
        self.IGNORE_COL = 2
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel(t.t("cities_title"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        input_frame = QFrame()
        input_frame.setObjectName("card")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(12)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText(t.t("cities_enter_name"))
        self.city_input.setMinimumWidth(250)
        self.city_input.returnPressed.connect(self._on_add)
        input_layout.addWidget(self.city_input)

        self.add_btn = QPushButton(t.t("cities_add"))
        self.add_btn.clicked.connect(self._on_add)
        input_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton(t.t("cities_delete"))
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self._on_delete)
        input_layout.addWidget(self.delete_btn)

        input_layout.addStretch()

        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #7F8C8D; font-size: 12px;")
        input_layout.addWidget(self.count_label)

        layout.addWidget(input_frame)

        status_frame = QFrame()
        status_frame.setObjectName("card")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(12, 8, 12, 8)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 12px; color: #7F8C8D;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        layout.addWidget(status_frame)

        search_frame = QFrame()
        search_frame.setObjectName("card")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(12, 8, 12, 8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t.t("common_search"))
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)

        layout.addWidget(search_frame)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "#", "City", "Ignore", "Available", "Registered", "Unknown", "Strength %", "Total"
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table)

    def refresh_data(self):
        self._all_cities = get_cities_table_data()
        self._populate_table(self._all_cities)

    def _populate_table(self, cities):
        self._loading = True
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(cities))
        for i, city in enumerate(cities):
            num_item = NumericTableWidgetItem(str(i + 1), i + 1)
            num_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, num_item)
            self.table.setItem(i, 1, QTableWidgetItem(city["name"]))

            ignore_item = QTableWidgetItem("")
            ignore_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
            ignore_item.setCheckState(Qt.Checked if city["ignore_it"] else Qt.Unchecked)
            ignore_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, self.IGNORE_COL, ignore_item)

            avail_item = NumericTableWidgetItem(str(city["available"]), city["available"])
            avail_item.setTextAlignment(Qt.AlignCenter)
            if city["available"] > 0:
                avail_item.setForeground(QColor("#27AE60"))
            self.table.setItem(i, 3, avail_item)

            reg_item = NumericTableWidgetItem(str(city["registered"]), city["registered"])
            reg_item.setTextAlignment(Qt.AlignCenter)
            if city["registered"] > 0:
                reg_item.setForeground(QColor("#E74C3C"))
            self.table.setItem(i, 4, reg_item)

            unk_item = NumericTableWidgetItem(str(city["unknown"]), city["unknown"])
            unk_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 5, unk_item)

            strength_item = NumericTableWidgetItem(f"{city['strength']:.1f}", city["strength"])
            strength_item.setTextAlignment(Qt.AlignCenter)
            s = city["strength"]
            if s >= 50:
                strength_item.setForeground(QColor("#E74C3C"))
            elif s >= 25:
                strength_item.setForeground(QColor("#F39C12"))
            else:
                strength_item.setForeground(QColor("#27AE60"))
            self.table.setItem(i, 6, strength_item)

            total_item = NumericTableWidgetItem(str(city["total"]), city["total"])
            total_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 7, total_item)

        self.table.setSortingEnabled(True)
        self._loading = False
        self.count_label.setText(f"{len(cities)} / {len(self._all_cities)}")

    def _on_item_changed(self, item):
        if self._loading or item.column() != self.IGNORE_COL:
            return
        name = self.table.item(item.row(), 1).text()
        handle_set_city_ignore(name, item.checkState() == Qt.Checked)

    def _on_search(self, text):
        query = text.strip().lower()
        if not query:
            self._populate_table(self._all_cities)
            return
        filtered = [c for c in self._all_cities if query in c["name"].lower()]
        self._populate_table(filtered)

    def _on_add(self):
        name = self.city_input.text().strip()
        if not name:
            return

        self.add_btn.setEnabled(False)
        self.city_input.setEnabled(False)
        self.status_label.setText(f"Adding '{name}'... checking domains against all checked niches")

        self._thread = AddCityThread(name)
        self._thread.progress.connect(self._on_progress)
        self._thread.finished.connect(self._on_finished)
        self._thread.start()

    def _on_progress(self, data):
        domain = data.get("domain", "")
        status = data.get("status", "")
        niche = data.get("niche", "")
        self.status_label.setText(f"Checking {domain} [{niche}]: {status}")

    def _on_finished(self, success, msg):
        self.add_btn.setEnabled(True)
        self.city_input.setEnabled(True)
        self.city_input.clear()

        if success:
            self.status_label.setText(f"✅ {t.t('cities_added_success')}")
        else:
            self.status_label.setText(f"❌ {t.t(msg)}")

        self.refresh_data()
        QMessageBox.information(self, t.t("common_success") if success else t.t("common_error"), t.t(msg))

    def _on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            return
        name = self.table.item(row, 1).text()
        reply = QMessageBox.question(
            self, t.t("common_delete"), f"{t.t('common_confirm_delete')}\n{name}",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = handle_delete_city(name)
            self.refresh_data()
            QMessageBox.information(self, t.t("common_success") if success else t.t("common_error"), msg)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()
