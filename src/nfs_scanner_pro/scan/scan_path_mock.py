"""蛇形扫描路径 Mock — Release 019。"""

from __future__ import annotations

from nfs_scanner_pro.scan.scan_point import ScanPointMock
from nfs_scanner_pro.scan.scan_task_config import ScanTaskConfig


class ScanPathMock:
    def __init__(self) -> None:
        self._config: ScanTaskConfig | None = None
        self._col_count = 91
        self._row_count = 71

    @property
    def col_count(self) -> int:
        return self._col_count

    @property
    def row_count(self) -> int:
        return self._row_count

    def generate_path(self, config: ScanTaskConfig) -> None:
        self._config = config
        if config.step_x > 0:
            cols = max(1, int(abs(config.end_x - config.start_x) / config.step_x) + 1)
        else:
            cols = 91
        rows = max(1, (config.total_points + cols - 1) // cols)
        self._col_count = cols
        self._row_count = rows

    def point_count(self) -> int:
        if self._config is None:
            return 0
        return self._config.total_points

    def index_to_grid(self, index: int) -> tuple[int, int]:
        """蛇形扫描：行优先，奇数行反向。"""
        if index <= 0:
            return 0, 0
        zero_based = index - 1
        row = zero_based // self._col_count
        col = zero_based % self._col_count
        if row % 2 == 1:
            col = self._col_count - 1 - col
        return row, col

    def get_point(self, index: int) -> ScanPointMock:
        if self._config is None:
            raise RuntimeError("Scan path not generated — call generate_path() first")
        index = max(0, min(index, self._config.total_points))
        row, col = self.index_to_grid(index) if index > 0 else (0, 0)
        cfg = self._config
        x = cfg.start_x + col * cfg.step_x
        y = cfg.start_y + row * cfg.step_y
        z = cfg.start_z + row * cfg.step_z
        return ScanPointMock.build(index, x, y, z, cfg.frequency)
