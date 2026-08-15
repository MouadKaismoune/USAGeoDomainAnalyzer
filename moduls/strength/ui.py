from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QFrame,
    QHeaderView
)
from PySide6.QtCore import Qt
from translator import translator as t
from moduls.strength.controller import get_strength_results


class StrengthWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        title = QLabel(t.t("strength_title"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        top_frame = QFrame()
        top_frame.setObjectName("card")
        top_layout = QHBoxLayout(top_frame)

        self.calc_btn = QPushButton(t.t("strength_calculate"))
        self.calc_btn.clicked.connect(self._on_calculate)
        top_layout.addWidget(self.calc_btn)
        top_layout.addStretch()

        self.count_label = QLabel("")
        top_layout.addWidget(self.count_label)
        layout.addWidget(top_frame)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "#", "Domain", "City", "Niche",
            t.t("strength_result") + " (City%)",
            t.t("strength_result") + " (Niche%)",
            "Score"
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def _on_calculate(self):
        results = get_strength_results()
        self.count_label.setText(f"{len(results)} domains")
        self.table.setRowCount(len(results))
        for i, r in enumerate(results):
            num_item = QTableWidgetItem(str(i + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, num_item)
            self.table.setItem(i, 1, QTableWidgetItem(r["domain"]))
            self.table.setItem(i, 2, QTableWidgetItem(r["city"]))
            self.table.setItem(i, 3, QTableWidgetItem(r["niche"]))
            self.table.setItem(i, 4, QTableWidgetItem(str(r["city_registered_pct"])))
            self.table.setItem(i, 5, QTableWidgetItem(str(r["niche_registered_pct"])))
            score_item = QTableWidgetItem(str(r["total_score"]))
            score_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 6, score_item)
