"""舵机系统 Mock — Release 018。"""

from __future__ import annotations

from typing import Any

from nfs_scanner_pro.devices.base import BaseDeviceMock
from nfs_scanner_pro.devices.device_types import DeviceType


class ServoSystemMock(BaseDeviceMock):
    def __init__(self) -> None:
        super().__init__(DeviceType.SERVO)
        self.current_probe = "Hx"
        self.hy_status = "待命"
        self.angle = "0.0°"
        self.offset = "X +0.02 / Y -0.01 mm"
        self.calibration = "已校准"
        self.profile = {"current_probe": self.current_probe}

    def switch_to_hx(self) -> str:
        self.current_probe = "Hx"
        self.hy_status = "待命"
        message = "Mock：已切换到 Hx"
        self._emit_message(message)
        return message

    def switch_to_hy(self) -> str:
        self.current_probe = "Hy"
        self.hy_status = "等待重新确认对齐"
        message = "Mock：已切换到 Hy，等待重新确认对齐"
        self._emit_message(message)
        return message

    def calibrate(self) -> str:
        self.calibration = "已校准"
        message = "Mock：Hx/Hy 校准完成"
        self._emit_message(message)
        return message

    def apply_offset(self) -> str:
        message = "Mock：偏移补偿已应用"
        self._emit_message(message)
        return message

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data.update(
            {
                "current_probe": self.current_probe,
                "hy_status": self.hy_status,
                "angle": self.angle,
                "offset": self.offset,
                "calibration": self.calibration,
            }
        )
        return data
