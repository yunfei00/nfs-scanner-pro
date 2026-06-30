"""分析 Mock 逻辑 — 参数与显示联动，无真实算法。"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer, Signal

from nfs_scanner_pro.analysis.analysis_dataset_mock import AnalysisDatasetMock
from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.analysis_state import AnalysisState

_LUT_TITLES = {
    "Turbo": "Turbo 色表",
    "Jet": "Jet 色表",
    "Viridis": "Viridis 色表",
    "Gray": "Gray 色表",
    "Hot": "Hot 色表",
}

_MODE_TITLES = {
    "幅度": "幅度 (dBm)",
    "相位": "相位 (°)",
    "实部": "实部",
    "虚部": "虚部",
}


@dataclass
class AnalysisDisplayParams:
    trace: str
    frequency: str
    mode: str
    lut: str
    vmin: float
    vmax: float
    opacity: int

    @classmethod
    def from_task(cls) -> AnalysisDisplayParams:
        t = mock_data.ANALYSIS_TASK
        return cls(
            trace=t["trace"],
            frequency=t["frequency"],
            mode=t["mode"],
            lut=t["lut"],
            vmin=float(t["vmin"]),
            vmax=float(t["vmax"]),
            opacity=int(t["opacity"]),
        )


class AnalysisMock(QObject):
    """分析参数 Mock 引擎。"""

    state_changed = Signal(object)
    display_changed = Signal(object)
    cursor_changed = Signal(dict)
    status_message = Signal(str, str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._state = AnalysisState.READY
        self._params = AnalysisDisplayParams.from_task()
        self._dataset = AnalysisDatasetMock.empty()
        self._cursor = copy.deepcopy(mock_data.ANALYSIS_CURSOR)
        self._cursor_locked = False
        self._export_timer = QTimer(self)
        self._export_timer.setSingleShot(True)
        self._export_timer.timeout.connect(self._finish_export)
        self._last_lut = self._params.lut

    @property
    def state(self) -> AnalysisState:
        return self._state

    @property
    def params(self) -> AnalysisDisplayParams:
        return self._params

    @property
    def dataset(self) -> AnalysisDatasetMock:
        return self._dataset

    @property
    def cursor(self) -> dict:
        return dict(self._cursor)

    @property
    def cursor_locked(self) -> bool:
        return self._cursor_locked

    def heatmap_opacity(self) -> float:
        return self._params.opacity / 100.0

    def color_scale_title(self) -> str:
        return _MODE_TITLES.get(self._params.mode, "幅度 (dBm)")

    def lut_label(self) -> str:
        return _LUT_TITLES.get(self._params.lut, self._params.lut)

    def apply_dataset(self, dataset: AnalysisDatasetMock) -> None:
        self._dataset = dataset
        if dataset.is_empty():
            self._set_state(AnalysisState.NOT_LOADED)
            self._emit_ready_status(found=False)
            return
        if dataset.frequency:
            self._params.frequency = dataset.frequency
        if dataset.trace:
            self._params.trace = dataset.trace
        self._cursor.update(dataset.cursor_readout(0))
        self._set_state(AnalysisState.LOADED)
        self.display_changed.emit(self._params)
        self.cursor_changed.emit(self.cursor)
        self._emit_ready_status(found=True)

    def select_scan_task(self, task_id: str) -> None:
        if self._dataset.task_id == task_id:
            return
        self._dataset.task_id = task_id
        self.status_message.emit(
            f"Mock：已加载分析数据源 {task_id}",
            self._status_extra1(),
            self._status_extra2(),
        )

    def apply_params(self, **kwargs) -> None:
        lut_changed = "lut" in kwargs and kwargs["lut"] != self._params.lut
        trace_changed = "trace" in kwargs and kwargs.get("trace") != self._params.trace
        freq_changed = "frequency" in kwargs and kwargs.get("frequency") != self._params.frequency
        for key, val in kwargs.items():
            if hasattr(self._params, key):
                setattr(self._params, key, val)
        self._cursor["frequency"] = self._params.frequency
        self._set_state(AnalysisState.PARAMS_CHANGED)
        self.display_changed.emit(self._params)
        self.cursor_changed.emit(self.cursor)
        if lut_changed:
            self.status_message.emit(
                f"Mock：LUT 已切换为 {self.lut_label()}",
                self._status_extra1(),
                self._status_extra2(),
            )
        elif trace_changed or freq_changed:
            self.status_message.emit(
                "Mock：分析参数已更新",
                self._status_extra1(),
                self._status_extra2(),
            )
        else:
            self._emit_status()

    def update_cursor_position(self, x: float, y: float) -> None:
        if self._cursor_locked:
            return
        self._cursor["x"] = x
        self._cursor["y"] = y
        rel = abs(math.sin(x * 0.03) * math.cos(y * 0.02))
        self._cursor["amp"] = -23.45 + rel * 6.0 - 3.0
        self._cursor["phase"] = 112.3 + rel * 15.0
        self.cursor_changed.emit(self.cursor)

    def toggle_cursor_lock(self) -> bool:
        self._cursor_locked = not self._cursor_locked
        return self._cursor_locked

    def set_cursor_locked(self, locked: bool) -> None:
        self._cursor_locked = locked

    def copy_cursor_readout(self) -> str:
        c = self._cursor
        return (
            f"X={c['x']:.2f} mm, Y={c['y']:.2f} mm, Z={c['z']:.2f} mm, "
            f"频率={c['frequency']}, 幅度={c['amp']:.2f} dBm, 相位={c['phase']:.1f}°"
        )

    def start_export(self, action: str) -> None:
        self._pending_export = action
        self._set_state(AnalysisState.EXPORTING)
        self.status_message.emit(f"Mock：{action}", self._status_extra1(), self._status_extra2())
        self._export_timer.start(400)

    def _finish_export(self) -> None:
        action = getattr(self, "_pending_export", "导出")
        self._set_state(AnalysisState.COMPLETED)
        self.status_message.emit(
            f"Mock：{action}",
            self._status_extra1(),
            self._status_extra2(),
        )
        self._set_state(AnalysisState.READY)

    def _set_state(self, state: AnalysisState) -> None:
        self._state = state
        self.state_changed.emit(state)

    def _emit_ready_status(self, *, found: bool) -> None:
        if found and self._dataset.task_id:
            text = f"分析就绪，已加载 Mock 扫描结果 {self._dataset.task_id}"
        else:
            text = "分析就绪，未发现 Mock 扫描结果"
        self.status_message.emit(text, self._status_extra1(), self._status_extra2())

    def _emit_status(self) -> None:
        self.status_message.emit(
            AnalysisState.READY.status_label,
            self._status_extra1(),
            self._status_extra2(),
        )

    def _status_extra1(self) -> str:
        if self._dataset.is_empty():
            return "Heatmap：未加载"
        return "Heatmap：已加载"

    def _status_extra2(self) -> str:
        if self._dataset.is_empty():
            return "ScanTask：—"
        points = self._dataset.total_points or mock_data.POINTS
        return f"ScanTask：{self._dataset.task_id} · {points} pts"
