"""分析数据加载状态 — Release 021。"""

from __future__ import annotations

from enum import Enum


class AnalysisDataState(str, Enum):
    EMPTY = "未发现扫描结果"
    LOADED = "已加载"
    ERROR = "读取错误"
