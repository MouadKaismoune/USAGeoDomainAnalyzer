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
from moduls.analyzer.controller import start_analysis, stop_analysis_thread
from moduls.niches.services import get_unchecked_niches, get_oldest_niche_names


_MAX_DELAY = 60


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

        # Body: niches + controls on the left, live results on the right
        body = QHBoxLayout()
        body.setSpacing(12)

        # ---------- Left column ----------
        left_col = QVBoxLayout()
        left_col.setSpacing(12)

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

        select_all_cb = QCheckBox(t.t("analyzer_select_all"))
        select_all_cb.setObjectName("AnalyzerNicheCheck")
        select_all_cb.stateChanged.connect(self._select_all)
        niches_layout.addWidget(select_all_cb)

        self.niches_scroll = QScrollArea()
        self.niches_scroll.setObjectName("AnalyzerNichesScroll")
        self.niches_scroll.setWidgetResizable(True)
        self.niches_scroll.setFrameShape(QFrame.NoFrame)
        self.niches_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.niches_container = QWidget()
        self.niches_container.setObjectName("AnalyzerNichesContainer")
        self.niches_checks_layout = QVBoxLayout(self.niches_container)
        self.niches_checks_layout.setContentsMargins(0, 0, 0, 0)
        self.niches_checks_layout.setSpacing(4)
        self.niches_scroll.setWidget(self.niches_container)
        niches_layout.addWidget(self.niches_scroll, 1)

        left_col.addWidget(niches_card, 1)

        control_card = QFrame()
        control_card.setObjectName("card")
        control_layout = QVBoxLayout(control_card)
        control_layout.setSpacing(10)

        delay_row = QHBoxLayout()
        delay_label = QLabel(t.t("analyzer_delay_label"))
        delay_label.setObjectName("AnalyzerDelayLabel")
        delay_row.addWidget(delay_label)
        delay_row.addStretch()
        self.delay_input = QLineEdit("2")
        self.delay_input.setFixedWidth(60)
        self.delay_input.setAlignment(Qt.AlignCenter)
        delay_row.addWidget(self.delay_input)
        control_layout.addLayout(delay_row)

        self.start_btn = QPushButton(t.t("analyzer_start"))
        self.start_btn.clicked.connect(self._on_start)
        control_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton(t.t("analyzer_stop"))
        self.stop_btn.setObjectName("delete_btn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        control_layout.addWidget(self.stop_btn)

        control_layout.addSpacing(6)

        oldest_row = QHBoxLayout()
        oldest_label = QLabel(t.t("analyzer_oldest_label"))
        oldest_label.setObjectName("AnalyzerDelayLabel")
        oldest_row.addWidget(oldest_label)
        oldest_row.addStretch()
        self.oldest_input = QLineEdit("5")
        self.oldest_input.setFixedWidth(60)
        self.oldest_input.setAlignment(Qt.AlignCenter)
        oldest_row.addWidget(self.oldest_input)
        control_layout.addLayout(oldest_row)

        self.oldest_btn = QPushButton(t.t("analyzer_start_oldest"))
        self.oldest_btn.clicked.connect(self._on_start_oldest)
        control_layout.addWidget(self.oldest_btn)

        left_col.addWidget(control_card)

        left_panel = QWidget()
        left_panel.setLayout(left_col)
        left_panel.setFixedWidth(300)
        body.addWidget(left_panel)

        # ---------- Right column ----------
        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        output_label = QLabel(t.t("common_live_output"))
        output_label.setObjectName("AnalyzerOutputLabel")
        right_col.addWidget(output_label)

        self.output = QTextEdit()
        self.output.setObjectName("AnalyzerOutput")
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 11))
        right_col.addWidget(self.output, 1)

        right_panel = QWidget()
        right_panel.setLayout(right_col)
        body.addWidget(right_panel, 1)

        layout.addLayout(body, 1)

        # ---------- Bottom: full-width progress bar ----------
        progress_card = QFrame()
        progress_card.setObjectName("card")
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setSpacing(8)

        progress_row = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_row.addWidget(self.progress_bar, 1)
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
            value = int(self.delay_input.text() or "2")
        except ValueError:
            value = 2
        return max(0, min(value, _MAX_DELAY))

    def _on_start(self):
        selected = self._get_selected_niches()
        if not selected:
            self._append_output("⚠️ No niches selected!", "warning")
            return

        self._start_analysis(selected)

    def _on_start_oldest(self):
        try:
            count = int(self.oldest_input.text() or "0")
        except ValueError:
            count = 0
        if count <= 0:
            self._append_output("⚠️ Enter a valid number of niches!", "warning")
            return

        niches = get_oldest_niche_names(count)
        if not niches:
            self._append_output("⚠️ No niches available to re-check!", "warning")
            return

        header = f"🕓 Selected {len(niches)} oldest niche(s) for re-check."
        self._start_analysis(niches, header=header)

    def _start_analysis(self, selected, header=None):
        delay = self._get_delay()

        self.output.clear()
        self.progress_bar.setValue(0)
        self.progress_label.setText("0%")
        self.domain_stat.setText("Available: 0 | Registered: 0")

        if header:
            self._append_output(header, "info")
        self._append_output(f"Starting analysis for {len(selected)} niches...", "info")
        self._append_output(f"Delay between cities: {delay}s", "dim")
        self._append_output("─" * 60, "rule")

        self._thread = start_analysis(selected_niches=selected, delay_cities=delay)
        self._thread.signal_data.connect(self._on_signal)
        self._thread.finished.connect(self._on_finished)
        self._thread.start()

        self.start_btn.setEnabled(False)
        self.oldest_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def _on_stop(self):
        stop_analysis_thread()
        self._append_output("\n⏹ Stopping... (finishing current domain check)", "error")

    def _on_signal(self, data):
        msg_type = data.get("type", "")

        if msg_type == "niche_reset":
            self._append_output(f"↺ Reset previous results for {data['niche']}", "dim")

        elif msg_type == "niche_start":
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
        self.oldest_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self._append_output("\n" + "=" * 60, "accent")
        if success:
            self._append_output("🎯 Analysis completed successfully!", "success")
        else:
            key = "common_unexpected_error" if msg == "unexpected_error" else msg
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
