"""扫描引擎 Mock — Release 019，不依赖 PySide6。"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Callable
from uuid import uuid4

from nfs_scanner_pro.devices import get_device_manager
from nfs_scanner_pro.scan.scan_path_mock import ScanPathMock
from nfs_scanner_pro.scan.scan_point import ScanPointMock
from nfs_scanner_pro.scan.scan_progress import ScanProgressMock
from nfs_scanner_pro.scan.scan_result_mock import ScanResultMock
from nfs_scanner_pro.scan.scan_result_persistence_mock import ScanResultPersistenceMock
from nfs_scanner_pro.scan.scan_state import ScanState
from nfs_scanner_pro.scan.scan_task_config import ScanTaskConfig

ProgressCallback = Callable[[ScanProgressMock], None]
StateCallback = Callable[[ScanState], None]
MessageCallback = Callable[[str], None]

_engine: ScanEngineMock | None = None


def get_scan_engine() -> ScanEngineMock:
    global _engine
    if _engine is None:
        _engine = ScanEngineMock()
    return _engine


class ScanEngineMock:
    TICK_POINTS_MIN = 50
    TICK_POINTS_MAX = 100

    def __init__(self, device_manager=None) -> None:
        self.device_manager = device_manager or get_device_manager()
        self.state = ScanState.NOT_READY
        self.config = ScanTaskConfig.default()
        self.path = ScanPathMock()
        self.progress = ScanProgressMock()
        self.result: ScanResultMock | None = None
        self.timer_interval_ms = 100
        self._device_snapshot: dict[str, Any] = {}
        self._stopped_by_user = False
        self._task_id = ""
        self._started_at = ""
        self._persistence = ScanResultPersistenceMock()
        self._progress_callbacks: list[ProgressCallback] = []
        self._state_callbacks: list[StateCallback] = []
        self._message_callbacks: list[MessageCallback] = []

    @property
    def stopped_by_user(self) -> bool:
        return self._stopped_by_user

    def on_progress(self, callback: ProgressCallback) -> None:
        self._progress_callbacks.append(callback)

    def on_state_changed(self, callback: StateCallback) -> None:
        self._state_callbacks.append(callback)

    def on_message(self, callback: MessageCallback) -> None:
        self._message_callbacks.append(callback)

    def prepare(self, config: ScanTaskConfig | None = None) -> None:
        self.config = config or ScanTaskConfig.from_mock_data()
        self.path.generate_path(self.config)
        self.progress.reset(self.config.total_points, state=ScanState.READY)
        self.state = ScanState.READY
        self.result = None
        self._stopped_by_user = False
        self._emit_state()

    def start(self) -> None:
        if not self.state.start_enabled():
            return
        self._task_id = f"ST-{uuid4().hex[:6].upper()}"
        self._started_at = datetime.now().isoformat(timespec="seconds")
        self._device_snapshot = self.device_manager.get_snapshot()
        self._stopped_by_user = False
        self.progress.reset(self.config.total_points, state=ScanState.SCANNING)
        self.progress.current_index = 0
        self.state = ScanState.SCANNING
        self._emit_state()
        self._emit_message("Mock：扫描已开始")

    def stop(self) -> None:
        if not self.state.stop_enabled():
            return
        self._stopped_by_user = True
        self.state = ScanState.STOPPING
        self.progress.state = ScanState.STOPPING
        self._emit_state()

    def finalize_stop(self) -> None:
        """UI 在 STOPPING 延迟后调用，完成停止或自然结束流程。"""
        if self._stopped_by_user:
            self.state = ScanState.READY
            self.progress.state = ScanState.READY
            self._emit_state()
            self._emit_message("Mock：扫描已停止")
            return
        self.state = ScanState.COMPLETED
        self.progress.state = ScanState.COMPLETED
        self.progress.current_index = self.config.total_points
        self.progress.percent = 100
        self.progress.remaining_time = "00:00:00"
        if self.progress.current_point is None:
            self.progress.current_point = self.path.get_point(self.config.total_points)
        self.result = ScanResultMock.create(
            task_id=self._task_id,
            config=self.config,
            device_snapshot=self._device_snapshot,
            final_index=self.config.total_points,
            status="completed",
            path=self.path,
            started_at=self._started_at,
        )
        self.result.preview_points = self._persistence.generate_preview_points(self.path)
        ok, detail = self._persistence.save_result(self.result)
        if ok:
            self._emit_message(f"Mock：扫描结果已保存到 {detail}")
        else:
            self._emit_message(f"Mock：扫描结果保存失败：{detail}")
        self._emit_progress()
        self._emit_state()
        self._emit_message("Mock：扫描完成")

    def pause(self) -> None:
        if self.state is not ScanState.SCANNING:
            return
        self.state = ScanState.PAUSED
        self.progress.state = ScanState.PAUSED
        self._emit_state()

    def resume(self) -> None:
        if self.state is not ScanState.PAUSED:
            return
        self.state = ScanState.SCANNING
        self.progress.state = ScanState.SCANNING
        self._emit_state()

    def reset(self) -> None:
        self.state = ScanState.NOT_READY
        self.progress.reset(0, state=ScanState.NOT_READY)
        self.result = None
        self._stopped_by_user = False
        self._emit_state()

    def tick(self) -> bool:
        """推进扫描进度。返回 True 表示仍在扫描中。"""
        if self.state is not ScanState.SCANNING:
            return False
        increment = random.randint(self.TICK_POINTS_MIN, self.TICK_POINTS_MAX)
        new_index = min(self.progress.current_index + increment, self.config.total_points)
        point = self.path.get_point(new_index)
        self.progress.update(new_index, point)
        self._emit_progress()
        if new_index >= self.config.total_points:
            self._stopped_by_user = False
            self.state = ScanState.STOPPING
            self.progress.state = ScanState.STOPPING
            self._emit_state()
            return False
        return True

    def current_progress(self) -> ScanProgressMock:
        return self.progress

    def current_point(self) -> ScanPointMock | None:
        return self.progress.current_point

    def is_running(self) -> bool:
        return self.state in (ScanState.SCANNING, ScanState.STOPPING)

    def _emit_progress(self) -> None:
        for callback in self._progress_callbacks:
            callback(self.progress)

    def _emit_state(self) -> None:
        for callback in self._state_callbacks:
            callback(self.state)

    def _emit_message(self, message: str) -> None:
        for callback in self._message_callbacks:
            callback(message)
