"""相机系统 Mock — Release 018。"""

from __future__ import annotations

from typing import Any

from nfs_scanner_pro.devices.base import BaseDeviceMock
from nfs_scanner_pro.devices.device_types import DeviceType


class CameraSystemMock(BaseDeviceMock):
    def __init__(self) -> None:
        super().__init__(DeviceType.CAMERA)
        self.interface = "USB3.0"
        self.resolution = "4096 × 3000"
        self.status_label = "预览就绪"
        self.capture_x = 0.0
        self.capture_y = 0.0
        self.capture_z = 5.00
        self.profile = {
            "interface": self.interface,
            "resolution": self.resolution,
        }

    def capture(self) -> str:
        message = "Mock：相机拍照完成"
        self._emit_message(message)
        return message

    def refresh_preview(self) -> str:
        message = "Mock：相机预览已刷新"
        self._emit_message(message)
        return message

    def open_settings(self) -> str:
        message = "Mock：打开相机设置"
        self._emit_message(message)
        return message

    def status_text(self) -> str:
        return self.status_label

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data.update(
            {
                "interface": self.interface,
                "resolution": self.resolution,
                "status": self.status_label,
                "capture_x": self.capture_x,
                "capture_y": self.capture_y,
                "capture_z": self.capture_z,
            }
        )
        return data
