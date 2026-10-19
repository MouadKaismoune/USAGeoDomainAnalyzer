from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QRect, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractButton,
    QComboBox,
    QMainWindow,
    QScrollBar,
    QSlider,
    QSpinBox,
    QWidget,
)

from app.core.config import CONFIG


class FramelessWindow(QMainWindow):
    """Frameless, translucent window with edge resizing and header dragging."""

    maximized_changed = Signal(bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._maximized = False
        self._normal_geometry: QRect | None = None
        self._drag_region: QWidget | None = None
        self._installed: set[int] = set()

        self._resize_edges: set[str] = set()
        self._press_global: QPoint | None = None
        self._press_frame: QPoint | None = None
        self._resize_start: QRect | None = None
        self._drag_offset: QPoint | None = None

        self.installEventFilter(self)

    def set_drag_region(self, widget: QWidget | None) -> None:
        self._drag_region = widget

    def setCentralWidget(self, widget: QWidget) -> None:
        super().setCentralWidget(widget)
        self._install_filter(widget)

    def _install_filter(self, widget: QWidget) -> None:
        for w in [widget, *widget.findChildren(QWidget)]:
            if id(w) in self._installed:
                continue
            w.installEventFilter(self)
            w.setMouseTracking(True)
            self._installed.add(id(w))

    def eventFilter(self, obj, event) -> bool:
        event_type = event.type()
        if event_type == QEvent.Type.MouseButtonPress:
            return self._on_press(obj, event)
        if event_type == QEvent.Type.MouseMove:
            return self._on_move(obj, event)
        if event_type == QEvent.Type.MouseButtonRelease:
            return self._on_release(obj, event)
        if event_type == QEvent.Type.MouseButtonDblClick:
            return self._on_double_click(obj, event)
        if event_type == QEvent.Type.Leave:
            if not self._resize_edges:
                self.unsetCursor()
            return False
        return False

    def _on_press(self, obj, event) -> bool:
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        if self._is_interactive(obj):
            return False
        global_pos = event.globalPosition().toPoint()

        edges = self._edge_zone(global_pos)
        if edges and not self._maximized:
            self._resize_edges = edges
            self._press_global = global_pos
            self._resize_start = self.frameGeometry()
            self._set_edge_cursor(edges)
            return True

        if self._is_in_drag_region(global_pos) and not self._maximized:
            self._press_global = global_pos
            self._drag_offset = global_pos - self.frameGeometry().topLeft()
            return True
        return False

    def _on_move(self, obj, event) -> bool:
        global_pos = event.globalPosition().toPoint()

        if self._resize_edges and self._resize_start and self._press_global:
            delta = global_pos - self._press_global
            new_rect = QRect(self._resize_start)
            edges = self._resize_edges
            if "left" in edges:
                new_rect.setLeft(self._resize_start.left() + delta.x())
            if "right" in edges:
                new_rect.setRight(self._resize_start.right() + delta.x())
            if "top" in edges:
                new_rect.setTop(self._resize_start.top() + delta.y())
            if "bottom" in edges:
                new_rect.setBottom(self._resize_start.bottom() + delta.y())
            self.setGeometry(self._enforce_min_size(new_rect))
            return True

        if self._drag_offset is not None:
            self.move(global_pos - self._drag_offset)
            return True

        if not self._maximized and not event.buttons():
            edges = self._edge_zone(global_pos)
            if edges and not self._is_interactive(obj):
                self._set_edge_cursor(edges)
            elif not edges:
                self.unsetCursor()
        return False

    def _on_release(self, obj, event) -> bool:
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        was_grabbing = bool(self._resize_edges or self._drag_offset)
        self._resize_edges = set()
        self._press_global = None
        self._resize_start = None
        self._drag_offset = None
        return was_grabbing

    def _on_double_click(self, obj, event) -> bool:
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        if self._is_interactive(obj):
            return False
        if self._is_in_drag_region(event.globalPosition().toPoint()):
            self.toggle_maximize()
            return True
        return False

    def _edge_zone(self, global_pos: QPoint) -> set[str]:
        frame = self.frameGeometry()
        x = global_pos.x() - frame.x()
        y = global_pos.y() - frame.y()
        margin = CONFIG.resize_margin
        edges: set[str] = set()
        if x <= margin:
            edges.add("left")
        if x >= frame.width() - margin:
            edges.add("right")
        if y <= margin:
            edges.add("top")
        if y >= frame.height() - margin:
            edges.add("bottom")
        return edges

    def _is_in_drag_region(self, global_pos: QPoint) -> bool:
        if self._drag_region is None:
            return False
        return self._drag_region.frameGeometry().contains(global_pos)

    def _is_interactive(self, obj) -> bool:
        cursor_widget = obj if isinstance(obj, QWidget) else None
        widget = cursor_widget
        while widget is not None and widget is not self:
            if isinstance(
                widget,
                (QAbstractButton, QScrollBar, QSlider, QSpinBox, QComboBox),
            ):
                return True
            widget = widget.parentWidget()
        return False

    def _set_edge_cursor(self, edges: set[str]) -> None:
        horizontal = bool(edges & {"left", "right"})
        vertical = bool(edges & {"top", "bottom"})
        if "left" in edges and "top" in edges:
            cursor = Qt.CursorShape.SizeFDiagCursor
        elif "right" in edges and "bottom" in edges:
            cursor = Qt.CursorShape.SizeFDiagCursor
        elif "right" in edges and "top" in edges:
            cursor = Qt.CursorShape.SizeBDiagCursor
        elif "left" in edges and "bottom" in edges:
            cursor = Qt.CursorShape.SizeBDiagCursor
        elif horizontal:
            cursor = Qt.CursorShape.SizeHorCursor
        elif vertical:
            cursor = Qt.CursorShape.SizeVerCursor
        else:
            cursor = Qt.CursorShape.ArrowCursor
        self.setCursor(cursor)

    def _enforce_min_size(self, rect: QRect) -> QRect:
        min_width, min_height = CONFIG.window_min_size
        if rect.width() < min_width:
            if "left" in self._resize_edges:
                rect.setLeft(rect.right() - min_width)
            else:
                rect.setRight(rect.left() + min_width)
        if rect.height() < min_height:
            if "top" in self._resize_edges:
                rect.setTop(rect.bottom() - min_height)
            else:
                rect.setBottom(rect.top() + min_height)
        return rect

    def toggle_maximize(self) -> None:
        if self._maximized:
            self._restore_from_maximized()
        else:
            self._maximize()

    def _maximize(self) -> None:
        self._normal_geometry = self.frameGeometry()
        screen = self.screen().availableGeometry()
        self.setGeometry(screen)
        self._maximized = True
        self.maximized_changed.emit(True)

    def _restore_from_maximized(self) -> None:
        if self._normal_geometry is not None:
            self.setGeometry(self._normal_geometry)
        self._maximized = False
        self.maximized_changed.emit(False)