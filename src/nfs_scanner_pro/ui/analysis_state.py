"""分析模块 Mock 状态 — Release 014。"""

from __future__ import annotations

from enum import Enum


class AnalysisState(str, Enum):
    NOT_LOADED = "未加载"
    LOADED = "已加载"
    READY = "分析就绪"
    PARAMS_CHANGED = "参数变更"
    EXPORTING = "导出中"
    COMPLETED = "完成"
    ERROR = "错误"

    @property
    def status_label(self) -> str:
        if self is AnalysisState.PARAMS_CHANGED:
            return "Mock：分析参数已更新"
        if self is AnalysisState.EXPORTING:
            return "Mock：导出中"
        if self is AnalysisState.COMPLETED:
            return "Mock：导出完成"
        return self.value
