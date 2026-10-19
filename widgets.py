from PySide6.QtWidgets import QTableWidgetItem


class NumericTableWidgetItem(QTableWidgetItem):
    def __init__(self, text, value=None):
        super().__init__(text)
        self._value = value if value is not None else self._parse(text)

    def _parse(self, text):
        try:
            return float(text.replace("%", "").strip())
        except (ValueError, TypeError):
            return 0.0

    def __lt__(self, other):
        if isinstance(other, NumericTableWidgetItem):
            return self._value < other._value
        return super().__lt__(other)


class StatusTableWidgetItem(QTableWidgetItem):
    STATUS_ORDER = {
        "available": 0,
        "registered": 1,
        "unknown": 2,
        "error": 3,
    }

    def __init__(self, text):
        super().__init__(text)
        lower = text.lower()
        self._order = 99
        for key, val in self.STATUS_ORDER.items():
            if key in lower:
                self._order = val
                break

    def __lt__(self, other):
        if isinstance(other, StatusTableWidgetItem):
            return self._order < other._order
        return super().__lt__(other)


class CheckedTableWidgetItem(QTableWidgetItem):
    def __init__(self, text, is_checked):
        super().__init__(text)
        self._checked = is_checked

    def __lt__(self, other):
        if isinstance(other, CheckedTableWidgetItem):
            return self._checked > other._checked
        return super().__lt__(other)


class DateTableWidgetItem(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)
        self._value = self._parse(text)

    def _parse(self, text):
        if not text:
            return None
        try:
            d, m, y = text.strip().split("-")
            return (int(y), int(m), int(d))
        except (ValueError, TypeError):
            return None

    def __lt__(self, other):
        if isinstance(other, DateTableWidgetItem):
            a, b = self._value, other._value
            if a is None and b is None:
                return False
            if a is None:
                return False
            if b is None:
                return True
            return a < b
        return super().__lt__(other)
