from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QFrame,
    QHeaderView, QLineEdit, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QTextCursor
from translator import translator as t
from moduls.maintenance.controller import get_unknown_domains_table, get_maintenance_stats
from moduls.maintenance.worker import RecheckThread
from moduls.maintenance.services import delete_unknown_domains
from widgets import NumericTableWidgetItem


class MaintenanceWidget(QWidget):
    done = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_domains = []
        self._thread = None
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel(t.t("maintenance_title"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        stats_frame = QFrame()
        stats_frame.setObjectName("card")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(24)

        self.count_label = QLabel("0")
        self.count_label.setObjectName("stat_value")
        self.count_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #F39C12;")
        stats_layout.addWidget(self.count_label)

        count_txt = QLabel(t.t("maintenance_unknown_count"))
        count_txt.setObjectName("stat_label")
        stats_layout.addWidget(count_txt)

        stats_layout.addStretch()

        self.cities_label = QLabel("0 cities")
        self.cities_label.setStyleSheet("font-size: 13px; color: #7F8C8D;")
        stats_layout.addWidget(self.cities_label)

        self.niches_label = QLabel("0 niches")
        self.niches_label.setStyleSheet("font-size: 13px; color: #7F8C8D;")
        stats_layout.addWidget(self.niches_label)

        layout.addWidget(stats_frame)

        control_frame = QFrame()
        control_frame.setObjectName("card")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setSpacing(12)

        self.recheck_btn = QPushButton(t.t("maintenance_recheck"))
        self.recheck_btn.clicked.connect(self._on_recheck)
        control_layout.addWidget(self.recheck_btn)

        self.stop_btn = QPushButton(t.t("analyzer_stop"))
        self.stop_btn.setObjectName("delete_btn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        control_layout.addWidget(self.stop_btn)

        self.delete_btn = QPushButton(t.t("maintenance_delete_all"))
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self._on_delete_all)
        control_layout.addWidget(self.delete_btn)

        control_layout.addStretch()

        delay_label = QLabel("Delay (sec):")
        delay_label.setStyleSheet("font-size: 12px; color: #7F8C8D;")
        control_layout.addWidget(delay_label)

        self.delay_input = QLineEdit("2")
        self.delay_input.setFixedWidth(50)
        self.delay_input.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.delay_input)

        layout.addWidget(control_frame)

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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "#", "Domain", "Status", "City", "Niche", "Date"
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table, 1)

        output_label = QLabel("Live Output:")
        output_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(output_label)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(120)
        self.output.setFont(QFont("Consolas", 11))
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E2E;
                color: #CDD6F4;
                border: 1px solid #45475A;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.output)

    def refresh_data(self):
        self._all_domains = get_unknown_domains_table()
        self._populate_table(self._all_domains)
        stats = get_maintenance_stats()
        self.count_label.setText(str(stats["count"]))
        self.cities_label.setText(f"{stats['cities']} cities")
        self.niches_label.setText(f"{stats['niches']} niches")

    def _populate_table(self, domains):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(domains))
        for i, d in enumerate(domains):
            num_item = NumericTableWidgetItem(str(i + 1), i + 1)
            num_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, num_item)
            self.table.setItem(i, 1, QTableWidgetItem(d["domain"]))

            status_item = QTableWidgetItem(d["status"])
            status_item.setForeground(QColor("#F39C12"))
            self.table.setItem(i, 2, status_item)

            self.table.setItem(i, 3, QTableWidgetItem(d["city"]))
            self.table.setItem(i, 4, QTableWidgetItem(d["niche"]))
            self.table.setItem(i, 5, QTableWidgetItem(d["date"]))

        self.table.setSortingEnabled(True)

    def _on_search(self, text):
        query = text.strip().lower()
        if not query:
            self._populate_table(self._all_domains)
            return
        filtered = [d for d in self._all_domains if query in d["domain"].lower()
                    or query in d["city"].lower()
                    or query in d["niche"].lower()]
        self._populate_table(filtered)

    def _on_recheck(self):
        self.output.clear()
        self.recheck_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.delete_btn.setEnabled(False)

        self._append_output(f"Starting re-check of {len(self._all_domains)} unknown domains...", "#3498DB")
        self._append_output("─" * 60, "#45475A")

        try:
            delay = max(0, int(self.delay_input.text() or "2"))
        except ValueError:
            delay = 2
        self._thread = RecheckThread(delay=delay)
        self._thread.signal_data.connect(self._on_signal)
        self._thread.finished.connect(self._on_finished)
        self._thread.start()

    def _on_stop(self):
        if self._thread:
            self._thread.stop()
        self._append_output("\nStopping...", "#E74C3C")

    def _on_signal(self, data):
        msg_type = data.get("type", "")
        if msg_type == "domain_check":
            domain = data["domain"]
            old = data["old_status"]
            new = data["new_status"]
            resolved = data["resolved"]
            current = data["current"]
            total = data["total"]
            fixed = data["fixed"]

            if resolved:
                color = "#A6E3A1"
                symbol = "✅"
            else:
                color = "#F9E2AF"
                symbol = "⚠️"

            self._append_output(
                f"  [{current}/{total}] {domain}: {old} → {new} {symbol}",
                color
            )

    def _on_finished(self, success, msg):
        self.recheck_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.delete_btn.setEnabled(True)

        self._append_output("\n" + "=" * 60, "#89B4FA")
        if success:
            if msg == "no_unknown":
                self._append_output("No unknown domains found!", "#A6E3A1")
            else:
                self._append_output(f"Re-check completed: {msg}", "#A6E3A1")
        else:
            self._append_output("Re-check stopped by user", "#F39C12")

        self.refresh_data()
        self.done.emit()

    def _on_delete_all(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, t.t("common_delete"),
            f"{t.t('common_confirm_delete')}\n{len(self._all_domains)} unknown domains?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            delete_unknown_domains()
            self.refresh_data()

    def _append_output(self, text, color="#CDD6F4"):
        self.output.setTextColor(QColor(color))
        self.output.append(text)
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()
