"""报告列表面板 — Release 015/022。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class _ReportListItem(QFrame):
    clicked = Signal()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self.clicked.emit()
        super().mousePressEvent(event)


class ReportListPanel(QWidget):
    report_selected = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("reportList")
        self.setFixedWidth(320)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        header = QLabel("报告列表", self)
        header.setObjectName("reportListHeader")
        header.setProperty("role", "listHeader")
        self._layout.addWidget(header)

        self._items: list[_ReportListItem] = []
        self._active_index = 0

    def set_reports(self, reports: list[dict]) -> None:
        for item in self._items:
            item.deleteLater()
        self._items.clear()
        while self._layout.count() > 1:
            item = self._layout.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for i, report in enumerate(reports):
            item = _ReportListItem(self)
            item.setObjectName(f"reportListItem{report.get('id', i)}")
            item.setProperty("role", "reportListItem")
            item.setProperty("active", i == 0)
            il = QVBoxLayout(item)
            il.setContentsMargins(16, 12, 16, 12)
            title = QLabel(report.get("name", ""), item)
            title.setProperty("role", "reportTitle")
            probe = report.get("probe", "")
            meta_text = report.get("meta") or f"{report.get('time', '')} · {probe}"
            meta = QLabel(meta_text, item)
            meta.setProperty("role", "reportMeta")
            il.addWidget(title)
            il.addWidget(meta)
            self._layout.insertWidget(self._layout.count(), item)
            self._items.append(item)
            item.clicked.connect(lambda ix=i: self._on_item_click(ix))

        self._layout.addStretch()
        self._active_index = 0
        if self._items:
            self.set_active(0)

    def _on_item_click(self, index: int) -> None:
        self.set_active(index)
        self.report_selected.emit(index)

    def set_active(self, index: int) -> None:
        self._active_index = index
        for i, item in enumerate(self._items):
            item.setProperty("active", i == index)
            item.style().unpolish(item)
            item.style().polish(item)
