"""报告列表面板 — Release 015。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from nfs_scanner_pro.ui import mock_data


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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("报告列表", self)
        header.setObjectName("reportListHeader")
        header.setProperty("role", "listHeader")
        layout.addWidget(header)

        self._items: list[_ReportListItem] = []
        for i, report in enumerate(mock_data.REPORTS):
            item = _ReportListItem(self)
            item.setObjectName(f"reportListItem{report['id']}")
            item.setProperty("role", "reportListItem")
            item.setProperty("active", i == 0)
            il = QVBoxLayout(item)
            il.setContentsMargins(16, 12, 16, 12)
            title = QLabel(report["name"], item)
            title.setProperty("role", "reportTitle")
            meta = QLabel(f"{report['time']} · {report['probe']}", item)
            meta.setProperty("role", "reportMeta")
            il.addWidget(title)
            il.addWidget(meta)
            layout.addWidget(item)
            self._items.append(item)
            item.clicked.connect(lambda ix=i: self._on_item_click(ix))

        layout.addStretch()
        self.set_active(0)

    def _on_item_click(self, index: int) -> None:
        self.set_active(index)
        self.report_selected.emit(index)

    def set_active(self, index: int) -> None:
        for i, item in enumerate(self._items):
            item.setProperty("active", i == index)
            item.style().unpolish(item)
            item.style().polish(item)
