import traceback

from PySide6.QtCore import QThread, Signal


class AnalysisThread(QThread):
    signal_data = Signal(dict)
    finished = Signal(bool, str)

    def __init__(self, selected_niches=None, delay_cities=2, delay_niches=30, parent=None):
        super().__init__(parent)
        self._selected_niches = selected_niches
        self._delay_cities = delay_cities
        self._delay_niches = delay_niches

    def stop(self):
        from moduls.analyzer.services import stop_analysis
        stop_analysis()

    def run(self):
        try:
            from moduls.analyzer.services import run_analysis
            success, msg = run_analysis(
                selected_niches=self._selected_niches,
                delay_between_cities=self._delay_cities,
                delay_between_niches=self._delay_niches,
                progress_callback=self._on_progress,
            )
        except Exception:
            traceback.print_exc()
            success, msg = False, "unexpected_error"
        self.finished.emit(success, msg)

    def _on_progress(self, **kwargs):
        self.signal_data.emit(kwargs)
