"""扫描任务 Mock 引擎 — QTimer 驱动，不接真实设备。"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer, Signal

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.scan_state import ScanState

TOTAL_SECONDS = 12 * 60 + 31  # 00:12:31
AMP_BASE = -23.45
AMP_JITTER = 3.0


@dataclass(frozen=True)
class ScanTick:
    point: int
    total: int
    percent: int
    x: float
    y: float
    z: float
    amp: float
    eta: str
    scene_x: float
    scene_y: float


def _format_eta(seconds: int) -> str:
    seconds = max(0, seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def point_to_grid(index: int) -> tuple[int, int]:
    """蛇形扫描：行优先，奇数行反向。"""
    col_count = mock_data.GRID_X
    row = index // col_count
    col = index % col_count
    if row % 2 == 1:
        col = col_count - 1 - col
    return row, col


def point_to_mm(row: int, col: int) -> tuple[float, float, float]:
    start = mock_data.SCAN_START_POSITION
    step = mock_data.SCAN_STEP
    x = start["x"] + col * step["x"]
    y = start["y"] + row * step["y"]
    z = start["z"]
    return x, y, z


def point_to_scene(row: int, col: int) -> tuple[float, float]:
    from nfs_scanner_pro.ui.scan_canvas_view import REGION_H, REGION_W, REGION_X, REGION_Y

    rel_x = col / max(1, mock_data.GRID_X - 1)
    rel_y = row / max(1, mock_data.GRID_Y - 1)
    return REGION_X + rel_x * REGION_W, REGION_Y + rel_y * REGION_H


def build_tick(point: int) -> ScanTick:
    total = mock_data.SCAN_TOTAL_POINTS
    point = max(0, min(point, total))
    row, col = point_to_grid(max(0, point - 1)) if point > 0 else (0, 0)
    x, y, z = point_to_mm(row, col)
    sx, sy = point_to_scene(row, col)
    percent = int(point * 100 / total) if total else 0
    remaining = int((total - point) / max(1, total) * TOTAL_SECONDS)
    amp = AMP_BASE + math.sin(point * 0.07) * AMP_JITTER * 0.6 + random.uniform(-0.8, 0.8)
    return ScanTick(
        point=point,
        total=total,
        percent=percent,
        x=x,
        y=y,
        z=z,
        amp=amp,
        eta=_format_eta(remaining),
        scene_x=sx,
        scene_y=sy,
    )


class ScanTaskMock(QObject):
    """Mock 扫描任务：100 ms 定时器，每 tick 增加 50~100 点。"""

    state_changed = Signal(object)  # ScanState
    tick_updated = Signal(object)  # ScanTick
    finished = Signal(bool)  # True=自然完成, False=用户停止

    TICK_MS = 100

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._state = ScanState.READY
        self._point = 0
        self._timer = QTimer(self)
        self._timer.setInterval(self.TICK_MS)
        self._timer.timeout.connect(self._on_tick)
        self._stop_timer = QTimer(self)
        self._stop_timer.setSingleShot(True)
        self._stop_timer.timeout.connect(self._finish_stop)
        self._completed_naturally = False

    @property
    def state(self) -> ScanState:
        return self._state

    @property
    def current_point(self) -> int:
        return self._point

    def reset_to_ready(self) -> None:
        self._timer.stop()
        self._stop_timer.stop()
        self._point = 0
        self._set_state(ScanState.READY)

    def start(self) -> None:
        if not self._state.start_enabled():
            return
        self._point = 0
        self._completed_naturally = False
        self._set_state(ScanState.SCANNING)
        self._emit_tick()
        self._timer.start()

    def stop(self) -> None:
        if self._state is not ScanState.SCANNING:
            return
        self._timer.stop()
        self._completed_naturally = False
        self._set_state(ScanState.STOPPING)
        self._stop_timer.start(500)

    def _finish_stop(self) -> None:
        if self._completed_naturally:
            self._set_state(ScanState.COMPLETED)
            self._emit_tick(force_eta_zero=True)
            self.finished.emit(True)
        else:
            self._set_state(ScanState.READY)
            self.finished.emit(False)

    def _on_tick(self) -> None:
        increment = random.randint(50, 100)
        self._point = min(self._point + increment, mock_data.SCAN_TOTAL_POINTS)
        self._emit_tick()
        if self._point >= mock_data.SCAN_TOTAL_POINTS:
            self._timer.stop()
            self._completed_naturally = True
            self._set_state(ScanState.STOPPING)
            self._stop_timer.start(500)

    def _emit_tick(self, *, force_eta_zero: bool = False) -> None:
        tick = build_tick(self._point)
        if force_eta_zero:
            tick = ScanTick(
                point=tick.point,
                total=tick.total,
                percent=100,
                x=tick.x,
                y=tick.y,
                z=tick.z,
                amp=tick.amp,
                eta="00:00:00",
                scene_x=tick.scene_x,
                scene_y=tick.scene_y,
            )
        self.tick_updated.emit(tick)

    def _set_state(self, state: ScanState) -> None:
        self._state = state
        self.state_changed.emit(state)

    def status_message(self) -> str:
        if self._state is ScanState.READY and self._point > 0:
            return "已停止"
        return self._state.status_label
