"""扫描页 — Scan Engine Mock 集成（Release 013/019）。"""

from __future__ import annotations

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QWidget

from nfs_scanner_pro.scan import ScanEngineMock, ScanState as EngineScanState, ScanTaskConfig, get_scan_engine
from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.scan_canvas_view import REGION_H, REGION_W, REGION_X, REGION_Y, ScanCanvasWidget
from nfs_scanner_pro.ui.scan_state import ScanState as UiScanState


def _to_ui_state(state: EngineScanState) -> UiScanState:
    if state is EngineScanState.PAUSED:
        return UiScanState.SCANNING
    mapping = {
        EngineScanState.NOT_READY: UiScanState.NOT_READY,
        EngineScanState.READY: UiScanState.READY,
        EngineScanState.SCANNING: UiScanState.SCANNING,
        EngineScanState.STOPPING: UiScanState.STOPPING,
        EngineScanState.COMPLETED: UiScanState.COMPLETED,
        EngineScanState.ERROR: UiScanState.ERROR,
    }
    return mapping.get(state, UiScanState.READY)


class ScanPage(ScanCanvasWidget):
    """扫描页：画布 + ScanEngineMock（UI QTimer 驱动 tick）。"""

    scan_state_changed = Signal(object)
    scan_status_updated = Signal(str, int, str, str)

    TICK_MS = 100
    STOP_DELAY_MS = 500

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._engine: ScanEngineMock = get_scan_engine()
        self._engine.prepare(ScanTaskConfig.from_mock_data())
        self._engine.on_state_changed(self._on_engine_state_changed)
        self._engine.on_progress(self._on_engine_progress)
        self._param_dock = None

        self._timer = QTimer(self)
        self._timer.setInterval(self.TICK_MS)
        self._timer.timeout.connect(self._on_timer_tick)

        self._stop_timer = QTimer(self)
        self._stop_timer.setSingleShot(True)
        self._stop_timer.timeout.connect(self._on_finalize_stop)

    def bind_parameter_dock(self, dock) -> None:
        self._param_dock = dock
        self._apply_params_editable(self._engine.state.params_editable())

    def start_scan_mock(self) -> None:
        if not self._engine.state.start_enabled():
            return
        self.reset_scan_visual()
        config = ScanTaskConfig.from_mock_data()
        self._engine.prepare(config)
        self._engine.start()
        self._timer.start()
        self._emit_status_from_engine()

    def stop_scan_mock(self) -> None:
        if not self._engine.state.stop_enabled():
            return
        self._timer.stop()
        self._engine.stop()
        self._stop_timer.start(self.STOP_DELAY_MS)

    def current_scan_state(self) -> UiScanState:
        return _to_ui_state(self._engine.state)

    def _on_timer_tick(self) -> None:
        still_running = self._engine.tick()
        if not still_running and self._engine.state is EngineScanState.STOPPING:
            self._timer.stop()
            self._stop_timer.start(self.STOP_DELAY_MS)

    def _on_finalize_stop(self) -> None:
        if self._engine.state is not EngineScanState.STOPPING:
            return
        stopped_by_user = self._engine.stopped_by_user
        self._engine.finalize_stop()
        progress = self._engine.current_progress()
        point = progress.current_point or self._engine.path.get_point(progress.current_index)
        sx, sy = self._point_to_scene(progress.current_index)
        scanning = self._engine.state is EngineScanState.SCANNING
        self.set_current_scan_point(
            progress.current_index,
            progress.total_points,
            sx,
            sy,
            scanning=scanning,
        )
        self.update_scan_coordinates(point.x, point.y, point.z, point.amplitude, lock=scanning)
        if self._engine.state is EngineScanState.COMPLETED:
            self.show_scan_complete_toast()
            self._emit_status(
                "扫描完成",
                100,
                f"扫描点：{progress.total_points} / {progress.total_points}",
                "预计剩余时间：00:00:00",
            )
        elif stopped_by_user:
            self._emit_status(
                "已停止",
                progress.percent,
                f"扫描点：{progress.current_index} / {progress.total_points}",
                f"预计剩余时间：{progress.remaining_time}",
            )
        self._apply_params_editable(self._engine.state.params_editable())

    def _on_engine_state_changed(self, state: EngineScanState) -> None:
        self._apply_params_editable(state.params_editable())
        if state is EngineScanState.READY and self._engine.progress.current_index == 0:
            self.reset_scan_visual()
        self.scan_state_changed.emit(_to_ui_state(state))
        self._emit_status_from_engine()

    def _on_engine_progress(self, progress) -> None:
        point = progress.current_point
        if point is None:
            return
        sx, sy = self._point_to_scene(progress.current_index)
        self.update_scan_coordinates(point.x, point.y, point.z, point.amplitude, lock=True)
        self.set_current_scan_point(
            progress.current_index,
            progress.total_points,
            sx,
            sy,
            scanning=True,
        )
        self._emit_status(
            "扫描中",
            progress.percent,
            f"扫描点：{progress.current_index} / {progress.total_points}",
            f"预计剩余时间：{progress.remaining_time}",
        )

    def _emit_status_from_engine(self) -> None:
        progress = self._engine.current_progress()
        state = self._engine.state
        if state is EngineScanState.SCANNING and progress.current_index == 0:
            self.set_current_scan_point(0, progress.total_points, REGION_X, REGION_Y, scanning=False)
        label = progress.as_status_text()
        if state is EngineScanState.COMPLETED:
            label = "扫描完成"
        self._emit_status(
            label,
            progress.percent,
            f"扫描点：{progress.current_index} / {progress.total_points}",
            self._eta_text(state, progress),
        )

    def _emit_status(self, state_text: str, percent: int, points: str, eta: str) -> None:
        self.scan_status_updated.emit(state_text, percent, points, eta)

    @staticmethod
    def _eta_text(state: EngineScanState, progress) -> str:
        if state is EngineScanState.COMPLETED:
            return "预计剩余时间：00:00:00"
        if state is EngineScanState.SCANNING:
            return f"预计剩余时间：{progress.remaining_time}"
        if state is EngineScanState.STOPPING:
            return "预计剩余时间：—"
        if state is EngineScanState.READY and progress.current_index > 0:
            return f"预计剩余时间：{progress.remaining_time}"
        return f"预计剩余时间：{mock_data.SCAN_DEFAULT_REMAINING}"

    def _point_to_scene(self, index: int) -> tuple[float, float]:
        row, col = self._engine.path.index_to_grid(index)
        cols = max(1, self._engine.path.col_count)
        rows = max(1, self._engine.path.row_count)
        rel_x = col / max(1, cols - 1)
        rel_y = row / max(1, rows - 1)
        return REGION_X + rel_x * REGION_W, REGION_Y + rel_y * REGION_H

    def _apply_params_editable(self, editable: bool) -> None:
        if self._param_dock is not None:
            self._param_dock.set_fields_locked(not editable)


__all__ = ["ScanPage", "ScanCanvasWidget"]
