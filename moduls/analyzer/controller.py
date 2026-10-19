from moduls.analyzer.worker import AnalysisThread
from moduls.analyzer.services import stop_analysis


def start_analysis(selected_niches=None, delay_cities=2, delay_niches=30):
    thread = AnalysisThread(
        selected_niches=selected_niches,
        delay_cities=delay_cities,
        delay_niches=delay_niches,
    )
    return thread


def stop_analysis_thread():
    stop_analysis()
