import traceback

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
        try:
            self._run()
        except Exception:
            traceback.print_exc()
            self.finished.emit(False, "unexpected_error")

    def _run(self):
        from moduls.maintenance.services import get_unknown_domains, update_domain_status
        from moduls.domains.rdap import check_domain_rdap, is_resolved
        import time

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
            new_status = check_domain_rdap(domain_name)

            resolved = is_resolved(new_status)

            if resolved:
                update_domain_status(d["id"], new_status)
                fixed += 1

            self.signal_data.emit({
                "type": "domain_check",
                "domain": domain_name,
                "old_status": d["status"],
                "new_status": new_status,
                "resolved": resolved,
                "current": i + 1,
                "total": total,
                "fixed": fixed,
            })

            if not resolved:
                time.sleep(1)
            else:
                time.sleep(self._delay)

        self.finished.emit(True, f"fixed:{fixed}/{total}")
