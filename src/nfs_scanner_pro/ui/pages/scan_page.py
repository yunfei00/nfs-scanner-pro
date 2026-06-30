"""扫描页 — Scan Module Mock（Release 013）。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.scan_canvas_view import ScanCanvasWidget
from nfs_scanner_pro.ui.scan_state import ScanState
from nfs_scanner_pro.ui.scan_task_mock import ScanTaskMock, ScanTick


class ScanPage(ScanCanvasWidget):
    """扫描页：画布 + Mock 扫描任务状态机。"""

    scan_state_changed = Signal(object)
    scan_status_updated = Signal(str, int, str, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._task = ScanTaskMock(self)
        self._task.state_changed.connect(self._on_state_changed)
        self._task.tick_updated.connect(self._on_tick)
        self._task.finished.connect(self._on_finished)
        self._param_dock = None

    def bind_parameter_dock(self, dock) -> None:
        self._param_dock = dock
        self._apply_params_editable(self._task.state.params_editable())

    def start_scan_mock(self) -> None:
        if not self._task.state.start_enabled():
            return
        self.reset_scan_visual()
        self._task.start()

    def stop_scan_mock(self) -> None:
        self._task.stop()

    def current_scan_state(self) -> ScanState:
        return self._task.state

    def _on_state_changed(self, state: ScanState) -> None:
        scanning = state is ScanState.SCANNING
        self._apply_params_editable(state.params_editable())
        if state is ScanState.READY and self._task.current_point == 0:
            self.reset_scan_visual()
        self.scan_state_changed.emit(state)
        tick = self._task.current_point
        total = mock_data.SCAN_TOTAL_POINTS
        self.scan_status_updated.emit(
            self._task.status_message(),
            int(tick * 100 / total) if total else 0,
            f"扫描点：{tick} / {total}",
            self._eta_for_state(state, tick, total),
        )
        if state is ScanState.SCANNING and tick == 0:
            self.update_scan_visual(0, total, 0, 0, scanning=False)

    def _on_tick(self, tick: ScanTick) -> None:
        self.update_scan_coordinates(tick.x, tick.y, tick.z, tick.amp, lock=True)
        self.update_scan_visual(
            tick.point, tick.total, tick.scene_x, tick.scene_y, scanning=True
        )
        self.scan_status_updated.emit(
            ScanState.SCANNING.status_label,
            tick.percent,
            f"扫描点：{tick.point} / {tick.total}",
            f"预计剩余时间：{tick.eta}",
        )

    def _on_finished(self, completed_naturally: bool) -> None:
        total = mock_data.SCAN_TOTAL_POINTS
        from nfs_scanner_pro.ui.scan_task_mock import build_tick

        if completed_naturally:
            last = build_tick(total)
            self.update_scan_visual(
                total, total, last.scene_x, last.scene_y, scanning=False
            )
            self.show_scan_complete_toast()
            self.scan_status_updated.emit(
                ScanState.COMPLETED.status_label,
                100,
                f"扫描点：{total} / {total}",
                "预计剩余时间：00:00:00",
            )
        else:
            point = self._task.current_point
            total = mock_data.SCAN_TOTAL_POINTS
            percent = int(point * 100 / total) if total else 0
            from nfs_scanner_pro.ui.scan_task_mock import build_tick

            last = build_tick(point)
            self.update_scan_visual(
                point, total, last.scene_x, last.scene_y, scanning=False
            )
            self.scan_status_updated.emit(
                "已停止",
                percent,
                f"扫描点：{point} / {total}",
                f"预计剩余时间：{last.eta}",
            )

    def _apply_params_editable(self, editable: bool) -> None:
        if self._param_dock is not None:
            self._param_dock.set_fields_locked(not editable)

    @staticmethod
    def _eta_for_state(state: ScanState, point: int, total: int) -> str:
        if state is ScanState.COMPLETED:
            return "预计剩余时间：00:00:00"
        if state is ScanState.SCANNING:
            return f"预计剩余时间：{mock_data.SCAN_DEFAULT_REMAINING}"
        if state is ScanState.STOPPING:
            return "预计剩余时间：—"
        return f"预计剩余时间：{mock_data.SCAN_DEFAULT_REMAINING}"


__all__ = ["ScanPage", "ScanCanvasWidget"]
