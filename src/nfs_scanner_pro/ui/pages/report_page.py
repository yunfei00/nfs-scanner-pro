"""报告页 — Report Data Source Mock（Release 015/022）。"""

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
        self._settings_panel = None
        self._breadcrumb = QLabel("", self)
        self._breadcrumb.setObjectName("breadcrumbBar")
        self._breadcrumb.setProperty("role", "pageBreadcrumb")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._breadcrumb)

        workspace = QHBoxLayout()
        workspace.setSpacing(0)

        self._list = ReportListPanel(self)
        self._list.report_selected.connect(self._mock.select_report)
        workspace.addWidget(self._list)

        self._preview = ReportPreviewPanel(self)
        workspace.addWidget(self._preview, stretch=1)

        self._mock.status_updated.connect(self.report_status_updated.emit)
        self._mock.report_changed.connect(self._on_report_changed)
        self._mock.preview_model_changed.connect(self._preview.show_model)
        self._mock.reports_list_changed.connect(self._list.set_reports)

        root.addLayout(workspace, stretch=1)

    def bind_settings_panel(self, panel) -> None:
        self._settings_panel = panel
        panel.settings_changed.connect(self._mock.apply_settings)
        self._mock.apply_settings(panel.get_settings())

    def refresh_data_source(self) -> None:
        if self._settings_panel is not None:
            self._mock.apply_settings(self._settings_panel.get_settings())
        self._mock.refresh_from_runtime()
        self._update_breadcrumb()

    def select_report(self, index: int) -> None:
        self._list.set_active(index)
        self._mock.select_report(index)
        self._update_breadcrumb()

    def refresh_preview(self) -> None:
        self._mock.refresh_preview()

    def create_draft(self) -> None:
        if self._settings_panel is not None:
            self._mock.apply_settings(self._settings_panel.get_settings())
        self._mock.create_draft()
        self._update_breadcrumb()

    def export_report(self, fmt: str) -> None:
        self._mock.start_export(fmt)

    def _on_report_changed(self, report: dict) -> None:
        self._update_breadcrumb(report.get("name", ""))

    def _update_breadcrumb(self, report_name: str | None = None) -> None:
        name = report_name or self._mock.current_report.get("name", "")
        if name:
            self._breadcrumb.setText(mock_data.get_breadcrumb_report(name))
        else:
            from nfs_scanner_pro import project_mock

            label = project_mock.project_display_name()
            self._breadcrumb.setText(f"报告 > {label}")
