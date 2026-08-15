from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox,
)

from translator import translator as t
from moduls.backup.services import (
    create_backup, delete_backup, get_database_info,
    list_backups, restore_backup,
)


class BackupWidget(QWidget):
    data_restored = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel(t.t("backup_title"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        action_card = QFrame()
        action_card.setObjectName("card")
        action_layout = QVBoxLayout(action_card)
        action_layout.setSpacing(10)

        subtitle = QLabel(t.t("backup_subtitle"))
        subtitle.setObjectName("AnalyzerDelayLabel")
        action_layout.addWidget(subtitle)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(t.t("backup_name_placeholder"))
        row.addWidget(self.name_input, 1)

        self.create_btn = QPushButton(t.t("backup_create"))
        self.create_btn.clicked.connect(self._on_create)
        row.addWidget(self.create_btn)
        action_layout.addLayout(row)

        self.db_info_label = QLabel("")
        self.db_info_label.setObjectName("AnalyzerDelayLabel")
        self.db_info_label.setWordWrap(True)
        action_layout.addWidget(self.db_info_label)

        layout.addWidget(action_card)

        list_card = QFrame()
        list_card.setObjectName("card")
        list_layout = QVBoxLayout(list_card)
        list_layout.setSpacing(10)

        header_row = QHBoxLayout()
        list_title = QLabel(t.t("backup_saved_label"))
        list_title.setObjectName("AnalyzerNichesTitle")
        header_row.addWidget(list_title)
        header_row.addStretch()
        self.count_label = QLabel("0")
        self.count_label.setObjectName("AnalyzerNichesCount")
        header_row.addWidget(self.count_label)
        list_layout.addLayout(header_row)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            t.t("backup_col_name"), t.t("backup_col_created"), t.t("backup_col_size")
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        list_layout.addWidget(self.table, 1)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)
        self.restore_btn = QPushButton(t.t("backup_restore"))
        self.restore_btn.clicked.connect(self._on_restore)
        buttons_row.addWidget(self.restore_btn)

        self.delete_btn = QPushButton(t.t("backup_delete"))
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self._on_delete)
        buttons_row.addWidget(self.delete_btn)

        self.refresh_btn = QPushButton(t.t("backup_refresh"))
        self.refresh_btn.setObjectName("secondary_btn")
        self.refresh_btn.clicked.connect(self.refresh_data)
        buttons_row.addWidget(self.refresh_btn)

        buttons_row.addStretch()
        list_layout.addLayout(buttons_row)

        layout.addWidget(list_card, 1)

        self.status_label = QLabel("")
        self.status_label.setObjectName("AnalyzerStatusLabel")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

    def refresh_data(self):
        info = get_database_info()
        self.db_info_label.setText(t.t("backup_db_info", path=info["path"], size=info["size"]))
        self._backups = list_backups()

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self._backups))
        for i, b in enumerate(self._backups):
            name_item = QTableWidgetItem(b["name"])
            name_item.setData(Qt.UserRole, b["path"])
            self.table.setItem(i, 0, name_item)
            self.table.setItem(i, 1, QTableWidgetItem(b["created"]))
            self.table.setItem(i, 2, QTableWidgetItem(b["size"]))
        self.table.setSortingEnabled(True)

        self.count_label.setText(str(len(self._backups)))
        if not self._backups:
            self.status_label.setText(t.t("backup_empty"))
            self.restore_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
        else:
            self.restore_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)

    def _selected_backup(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        item = self.table.item(rows[0].row(), 0)
        return {
            "path": item.data(Qt.UserRole),
            "name": item.text(),
        }

    def _show_status(self, text, error=False):
        self.status_label.setText(text)
        self.status_label.setProperty("accent", "error" if error else "success")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _on_create(self):
        label = self.name_input.text().strip()
        result = create_backup(label=label)
        if result.get("ok"):
            self.name_input.clear()
            self._show_status(t.t("backup_created", name=result["name"]))
        else:
            self._show_status(t.t("backup_created_fail", error=result.get("error", "")), error=True)
        self.refresh_data()

    def _on_restore(self):
        selected = self._selected_backup()
        if not selected:
            self._show_status(t.t("backup_no_selection"), error=True)
            return
        reply = QMessageBox.question(
            self, t.t("common_confirm_delete"),
            t.t("backup_restore_confirm", name=selected["name"]),
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        result = restore_backup(selected["path"])
        if result.get("ok"):
            self._show_status(t.t("backup_restored", name=selected["name"]))
            self.refresh_data()
            self.data_restored.emit()
        else:
            self._show_status(t.t("backup_restore_fail", error=result.get("error", "")), error=True)

    def _on_delete(self):
        selected = self._selected_backup()
        if not selected:
            self._show_status(t.t("backup_no_selection"), error=True)
            return
        reply = QMessageBox.question(
            self, t.t("common_delete"),
            t.t("backup_delete_confirm", name=selected["name"]),
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        result = delete_backup(selected["path"])
        if result.get("ok"):
            self._show_status(t.t("backup_deleted", name=selected["name"]))
        else:
            self._show_status(t.t("backup_delete_fail", error=result.get("error", "")), error=True)
        self.refresh_data()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()