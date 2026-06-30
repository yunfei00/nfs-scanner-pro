"""报告 Mock 引擎 — 数据源 / 草稿 / 预览 / 导出（Release 015/022）。"""

from __future__ import annotations

from copy import deepcopy

from PySide6.QtCore import QObject, QTimer, Signal

from nfs_scanner_pro import project_mock
from nfs_scanner_pro.report.report_data_source_mock import ReportDataSourceMock
from nfs_scanner_pro.report.report_draft_mock import ReportDraftMock
from nfs_scanner_pro.report.report_persistence_mock import ReportPersistenceMock
from nfs_scanner_pro.report.report_preview_model import ReportPreviewModel
from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.report_state import ReportState


class ReportMock(QObject):
    status_updated = Signal(str, str, str)
    report_changed = Signal(dict)
    preview_model_changed = Signal(object)
    reports_list_changed = Signal(list)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._state = ReportState.PREVIEW_DONE
        self._index = 0
        self._reports: list[dict] = []
        self._current_project = ""
        self._current_task = ""
        self._has_source = False
        self._settings = deepcopy(mock_data.REPORT_SETTINGS)
        self._data_source = ReportDataSourceMock()
        self._persistence = ReportPersistenceMock()
        self._export_timer = QTimer(self)
        self._export_timer.setSingleShot(True)
        self._export_timer.timeout.connect(self._finish_export)
        self._pending_export_msg = ""

    @property
    def state(self) -> ReportState:
        return self._state

    @property
    def current_report(self) -> dict:
        if not self._reports:
            return {}
        return dict(self._reports[self._index])

    @property
    def current_task_id(self) -> str:
        return self._current_task

    @property
    def has_source(self) -> bool:
        return self._has_source

    def apply_settings(self, settings: dict) -> None:
        self._settings.update(settings)

    def get_settings(self) -> dict:
        return deepcopy(self._settings)

    def refresh_from_runtime(self) -> None:
        preferred = project_mock.get_scan_project_name()
        project_name, tasks = self._data_source.resolve_project_and_tasks(preferred)
        self._current_project = project_name
        self._current_task = tasks[-1] if tasks else ""
        self._has_source = bool(self._current_task)

        reports: list[dict] = []
        if self._current_task:
            virtual = self._data_source.build_virtual_report_item(
                project_name,
                self._current_task,
            )
            if virtual is not None:
                reports.append(virtual)
        reports.extend(self._persistence.list_reports(project_name))

        if not reports and not self._has_source:
            self._reports = []
            self._index = 0
            self.reports_list_changed.emit(self._reports)
            self.status_updated.emit(
                "报告就绪，未发现 Mock 扫描结果",
                "",
                "",
            )
            self.preview_model_changed.emit(
                ReportPreviewModel.create_empty(
                    "未发现 Mock 扫描结果，请先完成一次 Mock 扫描。"
                )
            )
            return

        self._reports = reports
        self._index = 0
        self.reports_list_changed.emit(self._reports)

        if self._has_source:
            self._emit_enter_status()
        elif reports:
            self.status_updated.emit(
                f"报告就绪，已加载 {len(reports)} 份报告草稿",
                f"当前：{self.current_report.get('name', '—')}",
                "",
            )
        else:
            self.status_updated.emit(
                "报告就绪，未发现 Mock 扫描结果",
                "",
                "",
            )
        self._emit_current_preview()

    def select_report(self, index: int) -> None:
        if not self._reports or not 0 <= index < len(self._reports):
            return
        self._index = index
        report = self.current_report
        self._set_state(ReportState.PREVIEW_DONE)
        self.report_changed.emit(report)
        self._emit_current_preview()
        self.status_updated.emit(
            f"Mock：已选择报告 {report.get('name', '')}",
            f"当前：{report.get('name', '')}",
            "",
        )

    def refresh_preview(self) -> None:
        self._set_state(ReportState.PREVIEWING)
        if self._has_source:
            self._emit_current_preview()
        else:
            self.preview_model_changed.emit(
                ReportPreviewModel.create_empty(
                    "未发现 Mock 扫描结果，请先完成一次 Mock 扫描。"
                )
            )
        self.status_updated.emit(
            "Mock：报告预览已刷新",
            f"当前：{self.current_report.get('name', '—')}",
            "",
        )
        self._set_state(ReportState.PREVIEW_DONE)

    def create_draft(self) -> None:
        if not self._has_source or not self._current_task:
            self.status_updated.emit(
                "Mock：未发现扫描结果，请先完成一次 Mock 扫描",
                "",
                "",
            )
            return

        context = self._data_source.build_report_context(
            self._current_project,
            self._current_task,
        )
        dataset = context["dataset"]
        if not context["has_data"]:
            self.status_updated.emit(
                "Mock：没有可用扫描结果，无法创建报告",
                "",
                "",
            )
            return

        draft = ReportDraftMock.from_analysis_dataset(dataset, self._settings)
        ok, path_or_err = self._persistence.save_draft(draft)
        if not ok:
            self.status_updated.emit(
                f"Mock：报告草稿保存失败 — {path_or_err}",
                "",
                "",
            )
            return

        self.refresh_from_runtime()
        for i, item in enumerate(self._reports):
            if item.get("id") == draft.report_id:
                self._index = i
                break
        self.report_changed.emit(self.current_report)
        self._emit_current_preview()
        self.status_updated.emit(
            f"Mock：已创建报告草稿 {draft.report_name}",
            f"当前：{draft.report_name}",
            f"Mock：报告草稿已保存到 {path_or_err}",
        )

    def start_export(self, fmt: str) -> None:
        label = fmt.upper() if fmt.upper() in ("PDF", "WORD", "EXCEL") else fmt
        self._pending_export_msg = f"Mock：{label} 导出完成（未生成真实文件）"
        self._set_state(ReportState.EXPORTING)
        self.status_updated.emit(
            f"Mock：正在导出 {label}...",
            f"当前：{self.current_report.get('name', '—')}",
            "",
        )
        self._export_timer.start(400)

    def _finish_export(self) -> None:
        self._set_state(ReportState.EXPORT_DONE)
        self.status_updated.emit(
            self._pending_export_msg,
            f"当前：{self.current_report.get('name', '—')}",
            "",
        )
        self._set_state(ReportState.PREVIEW_DONE)

    def _emit_enter_status(self) -> None:
        task = self._current_task or mock_data.SCAN_TASK
        self.status_updated.emit(
            f"报告就绪，已加载 Mock 扫描结果 {task}",
            f"当前：{self.current_report.get('name', '—')}",
            "",
        )

    def _emit_current_preview(self) -> None:
        if not self._reports:
            self.preview_model_changed.emit(
                ReportPreviewModel.create_empty(
                    "未发现 Mock 扫描结果，请先完成一次 Mock 扫描。"
                )
            )
            return
        model = ReportPreviewModel.from_list_item(self.current_report)
        self.preview_model_changed.emit(model)
        self.report_changed.emit(self.current_report)

    def _set_state(self, state: ReportState) -> None:
        self._state = state
