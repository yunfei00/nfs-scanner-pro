"""扫描进度 Mock — Release 019。"""

from __future__ import annotations

from dataclasses import dataclass

from nfs_scanner_pro.scan.scan_point import ScanPointMock
from nfs_scanner_pro.scan.scan_state import ScanState

TOTAL_SECONDS = 12 * 60 + 31


def _format_eta(seconds: int) -> str:
    seconds = max(0, seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


@dataclass
class ScanProgressMock:
    state: ScanState = ScanState.NOT_READY
    current_index: int = 0
    total_points: int = 0
    percent: int = 0
    remaining_time: str = "00:12:31"
    current_point: ScanPointMock | None = None

    def reset(self, total_points: int = 0, *, state: ScanState = ScanState.READY) -> None:
        self.state = state
        self.current_index = 0
        self.total_points = total_points
        self.percent = 0
        self.remaining_time = _format_eta(TOTAL_SECONDS)
        self.current_point = None

    def update(self, index: int, point: ScanPointMock) -> None:
        self.current_index = index
        self.current_point = point
        total = max(1, self.total_points)
        self.percent = int(index * 100 / total)
        remaining = int((total - index) / total * TOTAL_SECONDS)
        self.remaining_time = _format_eta(remaining)

    def as_status_text(self) -> str:
        if self.state is ScanState.COMPLETED:
            return "扫描完成"
        if self.state is ScanState.SCANNING:
            return "扫描中"
        if self.state is ScanState.STOPPING:
            return "停止中"
        if self.state is ScanState.PAUSED:
            return "暂停"
        if self.state is ScanState.READY and self.current_index > 0:
            return "已停止"
        return self.state.value
