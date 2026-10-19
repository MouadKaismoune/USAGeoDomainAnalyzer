"""Lightweight table model for the Domains page.

``QTableWidget`` builds one ``QTableWidgetItem`` per cell, which becomes very
slow with tens of thousands of rows (≈150k objects for 16k rows). A
``QAbstractTableModel`` renders straight from the row dictionaries instead, so
filling the table is near-instant.

Each column declares how to display, colour and sort a row through plain
callables, keeping the page free of per-cell widget objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

_CENTER = int(Qt.AlignmentFlag.AlignCenter)
_LEFT = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

_STATUS_ORDER = {
    "available": 0,
    "registered": 1,
    "unknown": 2,
    "error": 3,
}

_MISSING_DATE = (9999, 99, 99)


def _status_order(status: str) -> int:
    lower = (status or "").lower()
    for key, value in _STATUS_ORDER.items():
        if key in lower:
            return value
    return 99


def _date_key(text: str):
    if not text:
        return _MISSING_DATE
    try:
        day, month, year = text.strip().split("-")
        return (int(year), int(month), int(day))
    except (ValueError, TypeError):
        return _MISSING_DATE


def _status_color(row: dict) -> str:
    status = str(row.get("status", "")).lower()
    if "available" in status and "registered" not in status:
        return "#27AE60"
    if "registered" in status:
        return "#E74C3C"
    return "#F39C12"


def _strength_color(row: dict) -> str:
    value = row.get("strength", 0)
    if value >= 50:
        return "#E74C3C"
    if value >= 25:
        return "#F39C12"
    return "#27AE60"


def _score_color(row: dict) -> str:
    value = row.get("total_score", 0)
    if value >= 50:
        return "#27AE60"
    if value >= 25:
        return "#F39C12"
    return "#E74C3C"


@dataclass(frozen=True)
class Column:
    title: str
    display: Callable[[dict], str]
    sort_key: Callable[[dict], object]
    align: int = _LEFT
    color: Callable[[dict], str] | None = None
    is_index: bool = False


class DomainTableModel(QAbstractTableModel):
    """Table model backed directly by a list of row dictionaries."""

    def __init__(self, columns: list[Column], parent=None) -> None:
        super().__init__(parent)
        self._columns = list(columns)
        self._rows: list[dict] = []
        self._sort_col = -1
        self._sort_order = Qt.SortOrder.AscendingOrder

    def set_rows(self, rows: list[dict]) -> None:
        self.beginResetModel()
        self._rows = list(rows)
        self._apply_sort()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._columns)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._columns[section].title
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        column = self._columns[index.column()]
        row = self._rows[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            if column.is_index:
                return str(index.row() + 1)
            return column.display(row)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return column.align
        if role == Qt.ItemDataRole.ForegroundRole and column.color is not None:
            color = column.color(row)
            if color:
                return QColor(color)
        return None

    def sort(self, column: int, order=Qt.SortOrder.AscendingOrder) -> None:
        if not 0 <= column < len(self._columns):
            return
        self._sort_col = column
        self._sort_order = order
        self.layoutAboutToBeChanged.emit()
        self._apply_sort()
        self.layoutChanged.emit()

    def _apply_sort(self) -> None:
        if self._sort_col < 0:
            return
        column = self._columns[self._sort_col]
        self._rows.sort(
            key=column.sort_key,
            reverse=self._sort_order == Qt.SortOrder.DescendingOrder,
        )


def all_domain_columns() -> list[Column]:
    return [
        Column("#", lambda r: "", lambda r: 0, align=_CENTER, is_index=True),
        Column("Domain", lambda r: r.get("domain", ""), lambda r: r.get("domain", "")),
        Column(
            "Status",
            lambda r: r.get("status", ""),
            lambda r: _status_order(r.get("status", "")),
            color=_status_color,
        ),
        Column("City", lambda r: r.get("city", ""), lambda r: r.get("city", "")),
        Column("Niche", lambda r: r.get("niche", ""), lambda r: r.get("niche", "")),
        Column(
            "Date",
            lambda r: r.get("date", ""),
            lambda r: _date_key(r.get("date", "")),
            align=_CENTER,
        ),
        Column(
            "City Str%",
            lambda r: f"{r.get('city_strength', 0):.1f}",
            lambda r: r.get("city_strength", 0),
            align=_CENTER,
        ),
        Column(
            "Niche Str%",
            lambda r: f"{r.get('niche_strength', 0):.1f}",
            lambda r: r.get("niche_strength", 0),
            align=_CENTER,
        ),
        Column(
            "Strength",
            lambda r: f"{r.get('strength', 0):.1f}",
            lambda r: r.get("strength", 0),
            align=_CENTER,
            color=_strength_color,
        ),
    ]


def strength_columns() -> list[Column]:
    return [
        Column("#", lambda r: "", lambda r: 0, align=_CENTER, is_index=True),
        Column("Domain", lambda r: r["domain"], lambda r: r["domain"]),
        Column("City", lambda r: r["city"], lambda r: r["city"]),
        Column("Niche", lambda r: r["niche"], lambda r: r["niche"]),
        Column(
            "City%",
            lambda r: str(r["city_registered_pct"]),
            lambda r: r["city_registered_pct"],
            align=_CENTER,
        ),
        Column(
            "Niche%",
            lambda r: str(r["niche_registered_pct"]),
            lambda r: r["niche_registered_pct"],
            align=_CENTER,
        ),
        Column(
            "Score",
            lambda r: str(r["total_score"]),
            lambda r: r["total_score"],
            align=_CENTER,
            color=_score_color,
        ),
    ]
