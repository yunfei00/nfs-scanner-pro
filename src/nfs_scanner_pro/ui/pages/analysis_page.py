"""分析页 — PCB + 热力图 + 扫描结果数据源 Mock（Release 014/021）。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel

from nfs_scanner_pro import project_mock
from nfs_scanner_pro.analysis.analysis_data_source_mock import AnalysisDataSourceMock
from nfs_scanner_pro.analysis.analysis_dataset_mock import AnalysisDatasetMock
from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.analysis_mock import AnalysisMock
from nfs_scanner_pro.ui.scan_canvas_view import PcbCanvasWidget, REGION_H, REGION_W, REGION_X, REGION_Y


class AnalysisPage(PcbCanvasWidget):
    analysis_status_updated = Signal(str, str, str)

    def __init__(self, parent=None) -> None:
        super().__init__(
            object_name="analysisPage",
            breadcrumb=mock_data.BREADCRUMB_ANALYSIS,
            show_minimap=True,
            show_handles=False,
            overlay_mode="cursor",
            show_crosshair=True,
            parent=parent,
        )
        self._mock = AnalysisMock(self)
        self._data_source = AnalysisDataSourceMock()
        self._control_panel = None
        self._data_source_panel = None
        self._grid_visible = True
        self._current_project = ""
        self._current_tasks: list[str] = []

        self._mock.display_changed.connect(self._apply_display)
        self._mock.cursor_changed.connect(self._on_cursor_changed)
        self._mock.status_message.connect(self.analysis_status_updated.emit)
        self._apply_display(self._mock.params)

    def bind_control_panel(self, panel) -> None:
        self._control_panel = panel
        panel.params_changed.connect(self._on_panel_params)
        panel.export_requested.connect(self._mock.start_export)
        panel.cursor_lock_changed.connect(self._on_cursor_lock)
        panel.cursor_copy_requested.connect(self._on_copy_cursor)

    def bind_data_source_panel(self, panel) -> None:
        self._data_source_panel = panel
        panel.scan_task_changed.connect(self._on_scan_task_selected)

    def refresh_data_source(self) -> None:
        preferred = project_mock.get_scan_project_name()
        project_name, tasks = self._data_source.resolve_project_and_tasks(preferred)
        self._current_project = project_name
        self._current_tasks = tasks
        selected = tasks[-1] if tasks else ""
        if selected:
            dataset = self._data_source.build_dataset(project_name, selected)
        else:
            dataset = AnalysisDatasetMock.empty(project_name)
        self._apply_dataset(dataset, tasks, selected)

    def toggle_grid(self) -> bool:
        self._grid_visible = not self._grid_visible
        self._view.set_grid_visible(self._grid_visible)
        return self._grid_visible

    def _on_scan_task_selected(self, task_id: str) -> None:
        if not task_id or not self._current_project:
            return
        dataset = self._data_source.build_dataset(self._current_project, task_id)
        self._apply_dataset(dataset, self._current_tasks, task_id)
        self._mock.select_scan_task(task_id)

    def _apply_dataset(
        self,
        dataset: AnalysisDatasetMock,
        tasks: list[str],
        selected_task: str,
    ) -> None:
        self._mock.apply_dataset(dataset)
        if self._data_source_panel is not None:
            self._data_source_panel.update_view(
                project_name=dataset.project_name or self._current_project,
                task_ids=tasks,
                selected_task=selected_task,
                dataset_loaded=not dataset.is_empty(),
                total_points=dataset.total_points,
                preview_points=len(dataset.preview_points),
                source_path=dataset.source_path,
            )
        if self._control_panel is not None and not dataset.is_empty():
            self._control_panel._trace_combo.setCurrentText(dataset.trace or "Trace 1")
            if dataset.frequency:
                idx = self._control_panel._freq_combo.findText(dataset.frequency)
                if idx >= 0:
                    self._control_panel._freq_combo.setCurrentIndex(idx)
        self._update_breadcrumb()
        self.set_analysis_empty_state(dataset.is_empty())

    def _on_panel_params(self, params: dict) -> None:
        self._mock.apply_params(**params)
        self._update_breadcrumb()

    def _apply_display(self, params) -> None:
        opacity = 0.18 if self._mock.dataset.is_empty() else self._mock.heatmap_opacity()
        self._view.set_heatmap_opacity(opacity)
        self._color_scale.set_title(self._mock.color_scale_title())

    def _update_breadcrumb(self) -> None:
        crumb = self.findChild(QLabel, "breadcrumbBar")
        if crumb is None:
            return
        params = self._mock.params
        task_id = self._mock.dataset.task_id or mock_data.SCAN_TASK
        region = self._mock.dataset.region_name or mock_data.REGION_NAME
        label = project_mock.project_display_name()
        crumb.setText(
            f"{label} > {region} > ScanTask {task_id} > {params.trace} > {params.frequency}"
        )

    def _on_cursor_changed(self, data: dict) -> None:
        self.update_cursor_readout(
            data["x"],
            data["y"],
            data["z"],
            data["frequency"],
            data["amp"],
            data["phase"],
        )
        if self._control_panel is not None:
            self._control_panel.update_cursor_panel(data)
        sx = REGION_X + (data["x"] - 10.0) / 180.0 * REGION_W
        sy = REGION_Y + (data["y"] + 150.0) / 140.0 * REGION_H
        self._view.set_crosshair_position(sx, sy)

    def _on_cursor_lock(self, locked: bool) -> None:
        self._mock.set_cursor_locked(locked)
        if self._control_panel is not None:
            self._control_panel.set_cursor_locked(locked)
        msg = "Mock：光标已锁定" if locked else "Mock：光标已解锁"
        self.analysis_status_updated.emit(
            msg,
            self._mock._status_extra1(),
            self._mock._status_extra2(),
        )

    def _on_copy_cursor(self) -> None:
        text = self._mock.copy_cursor_readout()
        print(f"[Mock UI] 复制读数：{text}", flush=True)
        self.analysis_status_updated.emit(
            "Mock：读数已复制",
            self._mock._status_extra1(),
            self._mock._status_extra2(),
        )

    def _on_mouse_moved(self, sx: float, sy: float) -> None:
        rel_x = (sx - REGION_X) / REGION_W if REGION_W else 0
        rel_y = (sy - REGION_Y) / REGION_H if REGION_H else 0
        x = 10.0 + rel_x * 180.0
        y = -150.0 + rel_y * 140.0
        self._mock.update_cursor_position(x, y)
        self._view.set_crosshair_position(sx, sy)
