"""报告页 — Report Module Mock（Release 015）。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.report_mock import ReportMock
from nfs_scanner_pro.ui.widgets.report_list_panel import ReportListPanel
from nfs_scanner_pro.ui.widgets.report_preview_panel import ReportPreviewPanel


class ReportPage(QWidget):
    report_status_updated = Signal(str, str, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("reportPage")

        self._mock = ReportMock(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        report = mock_data.REPORTS[0]
        crumb = QLabel(f"报告 > {mock_data.PROJECT_NAME} > {report['name']}", self)
        crumb.setObjectName("breadcrumbBar")
        crumb.setProperty("role", "pageBreadcrumb")
        root.addWidget(crumb)

        workspace = QHBoxLayout()
        workspace.setSpacing(0)

        self._list = ReportListPanel(self)
        self._list.report_selected.connect(self._mock.select_report)
        workspace.addWidget(self._list)

        self._preview = ReportPreviewPanel(self)
        workspace.addWidget(self._preview, stretch=1)

        self._mock.status_updated.connect(self.report_status_updated.emit)
        self._mock.report_changed.connect(self._preview.show_report)

        root.addLayout(workspace, stretch=1)

    def select_report(self, index: int) -> None:
        self._list.set_active(index)
        self._mock.select_report(index)

    def refresh_preview(self) -> None:
        self._mock.refresh_preview()

    def create_draft(self) -> None:
        self._mock.create_draft()

    def export_report(self, fmt: str) -> None:
        self._mock.start_export(fmt)
