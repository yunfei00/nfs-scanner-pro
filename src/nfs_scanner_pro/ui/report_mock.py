"""报告 Mock 引擎 — 选择/预览/导出，不生成真实文件。"""

from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.report_state import ReportState


class ReportMock(QObject):
    status_updated = Signal(str, str, str)
    report_changed = Signal(dict)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._state = ReportState.PREVIEW_DONE
        self._index = 0
        self._export_timer = QTimer(self)
        self._export_timer.setSingleShot(True)
        self._export_timer.timeout.connect(self._finish_export)
        self._pending_export_msg = ""

    @property
    def state(self) -> ReportState:
        return self._state

    @property
    def current_report(self) -> dict:
        return dict(mock_data.REPORTS[self._index])

    def select_report(self, index: int) -> None:
        if not 0 <= index < len(mock_data.REPORTS):
            return
        self._index = index
        report = self.current_report
        self._set_state(ReportState.PREVIEW_DONE)
        self.report_changed.emit(report)
        self.status_updated.emit(
            f"Mock：已选择报告 {report['name']}",
            f"当前：{report['name']}",
            "",
        )

    def refresh_preview(self) -> None:
        self._set_state(ReportState.PREVIEWING)
        report = self.current_report
        self.report_changed.emit(report)
        self.status_updated.emit(
            "Mock：报告预览已刷新",
            f"当前：{report['name']}",
            "",
        )
        self._set_state(ReportState.PREVIEW_DONE)

    def create_draft(self) -> None:
        self.status_updated.emit(
            "Mock：已创建新报告草稿",
            f"当前：{self.current_report['name']}",
            "",
        )

    def start_export(self, fmt: str) -> None:
        self._pending_export_msg = f"Mock：已导出 {fmt}"
        self._set_state(ReportState.EXPORTING)
        self.status_updated.emit(
            f"Mock：正在导出 {fmt}...",
            f"当前：{self.current_report['name']}",
            "",
        )
        self._export_timer.start(500)

    def _finish_export(self) -> None:
        self._set_state(ReportState.EXPORT_DONE)
        self.status_updated.emit(
            self._pending_export_msg,
            f"当前：{self.current_report['name']}",
            "",
        )
        self._set_state(ReportState.PREVIEW_DONE)

    def _set_state(self, state: ReportState) -> None:
        self._state = state
