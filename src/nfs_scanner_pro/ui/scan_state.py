"""扫描任务 Mock 状态枚举 — Release 013。"""

from __future__ import annotations

from enum import Enum


class ScanState(str, Enum):
    NOT_READY = "未就绪"
    READY = "准备就绪"
    SCANNING = "扫描中"
    STOPPING = "停止中"
    COMPLETED = "已完成"
    ERROR = "错误"

    @property
    def status_label(self) -> str:
        """底部状态栏主文案（与枚举值略有差异时覆盖）。"""
        if self is ScanState.COMPLETED:
            return "扫描完成"
        return self.value

    def start_enabled(self) -> bool:
        return self in (ScanState.READY, ScanState.COMPLETED)

    def stop_enabled(self) -> bool:
        return self is ScanState.SCANNING

    def params_editable(self) -> bool:
        return self in (ScanState.NOT_READY, ScanState.READY, ScanState.COMPLETED)
