"""报告模块 Mock 状态 — Release 015。"""

from __future__ import annotations

from enum import Enum


class ReportState(str, Enum):
    NOT_SELECTED = "未选择"
    PREVIEWING = "预览中"
    PREVIEW_DONE = "预览完成"
    EXPORTING = "导出中"
    EXPORT_DONE = "导出完成"
    ERROR = "错误"

    @property
    def status_label(self) -> str:
        if self is ReportState.PREVIEW_DONE:
            return "报告就绪"
        if self is ReportState.EXPORTING:
            return "Mock：导出中"
        if self is ReportState.EXPORT_DONE:
            return "Mock：导出完成"
        return self.value
