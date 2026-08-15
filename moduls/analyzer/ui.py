from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QProgressBar, QLabel, QFrame, QCheckBox,
    QScrollArea, QLineEdit, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QTextCursor
from config import config
from translator import translator as t
from app.ui.themes.theme import DARK, LIGHT
from moduls.analyzer.controller import start_analysis, stop_analysis_thread, get_analysis_info
from moduls.niches.services import get_unchecked_niches


def _text_color(key):
    theme = DARK if config.theme == "dark" else LIGHT
    return {
        "info": theme.primary,
        "accent": theme.primary,
        "success": theme.success,
        "error": theme.error,
        "warning": theme.warning,
        "dim": theme.text_secondary,
        "text": theme.text_primary,
        "rule": theme.border,
    }[key]


class AnalyzerWidget(QWidget):
    niche_done = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel(t.t("analyzer_title"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        niches_card = QFrame()
        niches_card.setObjectName("AnalyzerNichesCard")
        niches_layout = QVBoxLayout(niches_card)
        niches_layout.setContentsMargins(16, 14, 16, 14)
        niches_layout.setSpacing(8)

        niches_header = QHBoxLayout()
        niches_title = QLabel(t.t("analyzer_available_niches"))
        niches_title.setObjectName("AnalyzerNichesTitle")
        niches_header.addWidget(niches_title)
        niches_header.addStretch()
        self.niches_count_label = QLabel("")
        self.niches_count_label.setObjectName("AnalyzerNichesCount")
        niches_header.addWidget(self.niches_count_label)
        niches_layout.addLayout(niches_header)

        select_all_cb = QCheckBox("Select All")
        select_all_cb.setObjectName("AnalyzerNicheCheck")
        select_all_cb.stateChanged.connect(self._select_all)
        niches_layout.addWidget(select_all_cb)

        self.niches_scroll = QScrollArea()
        self.niches_scroll.setObjectName("AnalyzerNichesScroll")
        self.niches_scroll.setWidgetResizable(True)
        self.niches_scroll.setMaximumHeight(150)
        self.niches_scroll.setFrameShape(QFrame.NoFrame)
        self.niches_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.niches_container = QWidget()
        self.niches_container.setObjectName("AnalyzerNichesContainer")
        self.niches_checks_layout = QVBoxLayout(self.niches_container)
        self.niches_checks_layout.setContentsMargins(0, 0, 0, 0)
        self.niches_checks_layout.setSpacing(4)
        self.niches_scroll.setWidget(self.niches_container)
        niches_layout.addWidget(self.niches_scroll)

        layout.addWidget(niches_card)

        control_card = QFrame()
        control_card.setObjectName("card")
        control_layout = QHBoxLayout(control_card)
        control_layout.setSpacing(12)

        self.start_btn = QPushButton(t.t("analyzer_start"))
        self.start_btn.clicked.connect(self._on_start)
        control_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton(t.t("analyzer_stop"))
        self.stop_btn.setObjectName("delete_btn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        control_layout.addWidget(self.stop_btn)

        control_layout.addStretch()

        delay_label = QLabel("Delay (sec):")
        delay_label.setObjectName("AnalyzerDelayLabel")
        control_layout.addWidget(delay_label)

        self.delay_input = QLineEdit("2")
        self.delay_input.setFixedWidth(50)
        self.delay_input.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.delay_input)

        layout.addWidget(control_card)

        progress_card = QFrame()
        progress_card.setObjectName("card")
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setSpacing(8)

        progress_row = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_row.addWidget(self.progress_bar)
        self.progress_label = QLabel("0%")
        self.progress_label.setFixedWidth(50)
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_row.addWidget(self.progress_label)
        progress_layout.addLayout(progress_row)

        self.status_label = QLabel("")
        self.status_label.setObjectName("AnalyzerStatusLabel")
        progress_layout.addWidget(self.status_label)

        stats_row = QHBoxLayout()
        self.niche_stat = QLabel("Niches: 0/0")
        self.niche_stat.setObjectName("AnalyzerStatLabel")
        self.niche_stat.setProperty("accent", "primary")
        stats_row.addWidget(self.niche_stat)
        self.city_stat = QLabel("Cities: 0/0")
        self.city_stat.setObjectName("AnalyzerStatLabel")
        self.city_stat.setProperty("accent", "success")
        stats_row.addWidget(self.city_stat)
        stats_row.addStretch()
        self.domain_stat = QLabel("Available: 0 | Registered: 0")
        self.domain_stat.setObjectName("AnalyzerStatLabel")
        self.domain_stat.setProperty("accent", "warning")
        stats_row.addWidget(self.domain_stat)
        progress_layout.addLayout(stats_row)

        layout.addWidget(progress_card)

        output_label = QLabel("Live Output:")
        output_label.setObjectName("AnalyzerOutputLabel")
        layout.addWidget(output_label)

        self.output = QTextEdit()
        self.output.setObjectName("AnalyzerOutput")
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 11))
        layout.addWidget(self.output, 1)

        self._load_niches()

    def _load_niches(self):
        for i in range(self.niches_checks_layout.count()):
            child = self.niches_checks_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._checkboxes = []
        niches = get_unchecked_niches()

        for niche in niches:
            cb = QCheckBox(niche["name"])
            cb.setObjectName("AnalyzerNicheCheck")
            self.niches_checks_layout.addWidget(cb)
            self._checkboxes.append(cb)

        self.niches_checks_layout.addStretch()
        self.niches_count_label.setText(f"{len(niches)} unchecked")

    def _select_all(self, state):
        checked = bool(state)
        for cb in self._checkboxes:
            cb.setChecked(checked)

    def _get_selected_niches(self):
        return [cb.text() for cb in self._checkboxes if cb.isChecked()]

    def _get_delay(self):
        try:
            return max(0, int(self.delay_input.text() or "2"))
        except ValueError:
            return 2

    def _on_start(self):
        selected = self._get_selected_niches()
        if not selected:
            self._append_output("⚠️ No niches selected!", "warning")
            return

        delay = self._get_delay()

        self.output.clear()
        self.progress_bar.setValue(0)
        self.progress_label.setText("0%")
        self.domain_stat.setText("Available: 0 | Registered: 0")

        self._append_output(f"Starting analysis for {len(selected)} niches...", "info")
        self._append_output(f"Delay between cities: {delay}s", "dim")
        self._append_output("─" * 60, "rule")

        self._thread = start_analysis(selected_niches=selected, delay_cities=delay)
        self._thread.signal_data.connect(self._on_signal)
        self._thread.finished.connect(self._on_finished)
        self._thread.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def _on_stop(self):
        stop_analysis_thread()
        self._append_output("\n⏹ Stopping... (finishing current domain check)", "error")

    def _on_signal(self, data):
        msg_type = data.get("type", "")

        if msg_type == "niche_start":
            niche = data["niche"]
            idx = data["niche_index"]
            total = data["total_niches"]
            self.progress_bar.setValue(0)
            self.progress_label.setText("0%")
            self._append_output(f"\n🔍 [{idx}/{total}] {niche}", "accent")
            self._append_output("─" * 60, "rule")
            self.niche_stat.setText(f"Niches: {idx}/{total}")

        elif msg_type == "domain_check":
            domain = data["domain"]
            status = data["status"]
            city_idx = data["city_index"]
            total_cities = data["total_cities"]

            if "✅" in status:
                color = "success"
            elif "❌" in status:
                color = "error"
            else:
                color = "warning"

            self._append_output(f"  {domain}: {status}", color)

            self.city_stat.setText(f"Cities: {city_idx}/{total_cities}")

            pct = int((city_idx / total_cities) * 100)
            self.progress_bar.setValue(pct)
            self.progress_label.setText(f"{pct}%")

            self.status_label.setText(f"Checking: {domain}")

        elif msg_type == "niche_done":
            niche = data["niche"]
            avail = data["available"]
            reg = data["registered"]
            unk = data["unknown"]
            self.progress_bar.setValue(100)
            self.progress_label.setText("100%")
            self._append_output("", "text")
            self._append_output(
                f"  ✅ Done: {niche} → Available: {avail} | Registered: {reg} | Unknown: {unk}",
                "success"
            )
            self._append_output("─" * 60, "rule")
            self.domain_stat.setText(f"Available: {avail} | Registered: {reg}")
            self.niche_done.emit()

        elif msg_type == "delay":
            seconds = data["seconds"]
            next_niche = data["next_niche"]
            self._append_output(f"\n⏳ Waiting {seconds}s before next niche...", "dim")

    def _append_output(self, text, key="text"):
        self.output.setTextColor(QColor(_text_color(key)))
        self.output.append(text)
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    def _on_finished(self, success, msg):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self._append_output("\n" + "=" * 60, "accent")
        if success:
            self._append_output("🎯 Analysis completed successfully!", "success")
        else:
            key = f"analyzer_{msg}"
            from translator import translator
            translated = translator.t(key)
            self._append_output(f"⚠️ {translated}", "warning")

        self.progress_bar.setValue(100 if success else self.progress_bar.value())
        self.progress_label.setText("100%" if success else "Stopped")
        self.status_label.setText("Finished" if success else "Stopped")

        self._load_niches()
        self.niche_done.emit()

    def showEvent(self, event):
        super().showEvent(event)
        self._load_niches()
