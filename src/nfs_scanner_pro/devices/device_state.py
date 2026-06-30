"""设备状态枚举 — Release 018。"""

from __future__ import annotations

from enum import Enum


class DeviceState(str, Enum):
    UNCONFIGURED = "未配置"
    DISCONNECTED = "未连接"
    CONNECTING = "连接中"
    CONNECTED = "已连接"
    BUSY = "忙碌"
    ERROR = "错误"
    DISABLED = "禁用"

    def chip_status(self) -> str:
        """设备状态栏 chip 属性：connected / disconnected / error。"""
        if self is DeviceState.ERROR:
            return "error"
        if self in (DeviceState.CONNECTED, DeviceState.BUSY, DeviceState.CONNECTING):
            return "connected"
        return "disconnected"
