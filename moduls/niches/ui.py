from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel,
    QFrame, QHeaderView, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from translator import translator as t
from moduls.niches.controller import (
    get_niches_table_data, handle_add_niche, handle_delete_niche, handle_reset_niche, handle_set_niche_ignore
)
from widgets import NumericTableWidgetItem, CheckedTableWidgetItem, DateTableWidgetItem


class NichesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_niches = []
        self._loading = False
        self.IGNORE_COL = 2
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel(t.t("niches_title"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        input_frame = QFrame()
        input_frame.setObjectName("card")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(12)

        self.niche_input = QLineEdit()
        self.niche_input.setPlaceholderText(t.t("niches_enter_name"))
        self.niche_input.setMinimumWidth(250)
        self.niche_input.returnPressed.connect(self._on_add)
        input_layout.addWidget(self.niche_input)

        self.add_btn = QPushButton(t.t("niches_add"))
        self.add_btn.clicked.connect(self._on_add)
        input_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton(t.t("niches_delete"))
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self._on_delete)
        input_layout.addWidget(self.delete_btn)

        self.export_btn = QPushButton(t.t("common_export"))
        self.export_btn.clicked.connect(self._on_export)
        input_layout.addWidget(self.export_btn)

        self.reset_btn = QPushButton(t.t("niches_reset_data"))
        self.reset_btn.setObjectName("delete_btn")
        self.reset_btn.clicked.connect(self._on_reset)
        input_layout.addWidget(self.reset_btn)

        input_layout.addStretch()

        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #7F8C8D; font-size: 12px;")
        input_layout.addWidget(self.count_label)

        layout.addWidget(input_frame)

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
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "#", "Niche", "Ignore", "Checked", "Date", "Available",
            "Registered", "Unknown", "Strength %", "Total"
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
        self._all_niches = get_niches_table_data()
        self._populate_table(self._all_niches)

    def _populate_table(self, niches):
        self._loading = True
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(niches))
        for i, niche in enumerate(niches):
            num_item = NumericTableWidgetItem(str(i + 1), i + 1)
            num_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, num_item)
            self.table.setItem(i, 1, QTableWidgetItem(niche["name"]))

            ignore_item = QTableWidgetItem("")
            ignore_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
            ignore_item.setCheckState(Qt.Checked if niche["ignore_it"] else Qt.Unchecked)
            ignore_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, self.IGNORE_COL, ignore_item)

            checked = niche["is_checked"]
            checked_item = CheckedTableWidgetItem("✅" if checked else "⏳", checked)
            checked_item.setTextAlignment(Qt.AlignCenter)
            if not checked:
                checked_item.setForeground(QColor("#F39C12"))
            else:
                checked_item.setForeground(QColor("#27AE60"))
            self.table.setItem(i, 3, checked_item)

            date_item = DateTableWidgetItem(niche.get("checked_date", "") or "")
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, date_item)

            avail_item = NumericTableWidgetItem(str(niche["available"]), niche["available"])
            avail_item.setTextAlignment(Qt.AlignCenter)
            if niche["available"] > 0:
                avail_item.setForeground(QColor("#27AE60"))
            self.table.setItem(i, 5, avail_item)

            reg_item = NumericTableWidgetItem(str(niche["registered"]), niche["registered"])
            reg_item.setTextAlignment(Qt.AlignCenter)
            if niche["registered"] > 0:
                reg_item.setForeground(QColor("#E74C3C"))
            self.table.setItem(i, 6, reg_item)

            unk_item = NumericTableWidgetItem(str(niche["unknown"]), niche["unknown"])
            unk_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 7, unk_item)

            strength_item = NumericTableWidgetItem(f"{niche['strength']:.1f}", niche["strength"])
            strength_item.setTextAlignment(Qt.AlignCenter)
            s = niche["strength"]
            if s >= 50:
                strength_item.setForeground(QColor("#E74C3C"))
            elif s >= 25:
                strength_item.setForeground(QColor("#F39C12"))
            else:
                strength_item.setForeground(QColor("#27AE60"))
            self.table.setItem(i, 8, strength_item)

            total_item = NumericTableWidgetItem(str(niche["total"]), niche["total"])
            total_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 9, total_item)

        self.table.setSortingEnabled(True)
        self._loading = False
        self.count_label.setText(f"{len(niches)} / {len(self._all_niches)}")

    def _on_item_changed(self, item):
        if self._loading or item.column() != self.IGNORE_COL:
            return
        name = self.table.item(item.row(), 1).text()
        handle_set_niche_ignore(name, item.checkState() == Qt.Checked)

    def _on_search(self, text):
        query = text.strip().lower()
        if not query:
            self._populate_table(self._all_niches)
            return
        filtered = [n for n in self._all_niches if query in n["name"].lower()]
        self._populate_table(filtered)

    def _on_add(self):
        name = self.niche_input.text().strip()
        if not name:
            return
        success, msg = handle_add_niche(name)
        if success:
            self.niche_input.clear()
            self.refresh_data()
        QMessageBox.information(self, t.t("common_success") if success else t.t("common_error"), msg)

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
            success, msg = handle_delete_niche(name)
            self.refresh_data()
            QMessageBox.information(self, t.t("common_success") if success else t.t("common_error"), msg)

    def _on_export(self):
        path, _ = QFileDialog.getSaveFileName(self, t.t("common_export"), "niches.csv", "CSV Files (*.csv)")
        if not path:
            return
        headers = ["#", "Niche", "Ignore", "Checked", "Date", "Available", "Registered", "Unknown", "Strength %", "Total"]
        with open(path, "w", encoding="utf-8") as f:
            f.write(",".join(headers) + "\n")
            for i, niche in enumerate(self._all_niches):
                row = [
                    str(i + 1),
                    niche["name"],
                    "Yes" if niche["ignore_it"] else "No",
                    "Yes" if niche["is_checked"] else "No",
                    niche.get("checked_date", "") or "",
                    str(niche["available"]),
                    str(niche["registered"]),
                    str(niche["unknown"]),
                    f"{niche['strength']:.1f}",
                    str(niche["total"]),
                ]
                f.write(",".join(row) + "\n")
        QMessageBox.information(self, t.t("common_success"), f"Exported to {path}")

    def _on_reset(self):
        row = self.table.currentRow()
        if row < 0:
            return
        name = self.table.item(row, 1).text()
        reply = QMessageBox.question(
            self, t.t("niches_reset_data"),
            t.t("niches_reset_confirm", name=name),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = handle_reset_niche(name)
            self.refresh_data()
            QMessageBox.information(self, t.t("common_success") if success else t.t("common_error"), msg)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()
