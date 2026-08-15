from PySide6.QtCore import QThread, Signal


class RecheckThread(QThread):
    signal_data = Signal(dict)
    finished = Signal(bool, str)

    def __init__(self, delay=2, parent=None):
        super().__init__(parent)
        self._delay = delay
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        from moduls.maintenance.services import get_unknown_domains, update_domain_status
        from moduls.analyzer.services import check_domain_rdap
        from database import db
        from database.models import NicheSummaryModel
        import time

        summary_model = NicheSummaryModel(db)
        domains = get_unknown_domains()
        if not domains:
            self.finished.emit(True, "no_unknown")
            return

        total = len(domains)
        fixed = 0
        for i, d in enumerate(domains):
            if not self._running:
                self.finished.emit(False, "stopped")
                return

            domain_name = d["domain"]
            niche = d["niche"]
            new_status = check_domain_rdap(domain_name)

            status_lower = new_status.lower()
            is_resolved = "available" in status_lower or "registered" in status_lower

            if is_resolved:
                update_domain_status(d["id"], new_status)
                fixed += 1

                if "available" in status_lower and "registered" not in status_lower:
                    summary_model.adjust_counts(niche, available_delta=1, unknown_delta=-1)
                elif "registered" in status_lower:
                    summary_model.adjust_counts(niche, not_available_delta=1, unknown_delta=-1)

            self.signal_data.emit({
                "type": "domain_check",
                "domain": domain_name,
                "old_status": d["status"],
                "new_status": new_status,
                "resolved": is_resolved,
                "current": i + 1,
                "total": total,
                "fixed": fixed,
            })

            if not is_resolved:
                time.sleep(1)
            else:
                time.sleep(self._delay)

        self.finished.emit(True, f"fixed:{fixed}/{total}")
