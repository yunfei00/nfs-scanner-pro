"""运动平台 Mock — Release 018。"""

from __future__ import annotations

from typing import Any

from nfs_scanner_pro.devices.base import BaseDeviceMock
from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.device_types import DeviceType


class MotionControllerMock(BaseDeviceMock):
    def __init__(self) -> None:
        super().__init__(DeviceType.MOTION)
        self.port = "COM6"
        self.baudrate = 115200
        self.x = 45.20
        self.y = -28.30
        self.z = 5.00
        self.speed = 1000
        self.travel_x = "0 ~ 200"
        self.travel_y = "0 ~ -300"
        self.travel_z = "0 ~ 10"
        self.profile = {
            "port": self.port,
            "baudrate": self.baudrate,
            "speed": self.speed,
        }

    def home(self) -> str:
        self._set_state(DeviceState.BUSY)
        message = "Mock：运动平台回零命令已触发"
        self._emit_message(message)
        self._set_state(DeviceState.CONNECTED)
        return message

    def stop(self) -> str:
        message = "Mock：运动平台停止命令已触发"
        self._emit_message(message)
        self._set_state(DeviceState.CONNECTED)
        return message

    def refresh_position(self) -> str:
        message = (
            f"Mock：运动平台位置 X {self.x:.2f} / Y {self.y:.2f} / Z {self.z:.2f} mm"
        )
        self._emit_message(message)
        return message

    def jog(self, axis: str, direction: str) -> str:
        delta_map = {"x": 1.0, "y": 1.0, "z": 0.1}
        axis_key = axis.lower()
        sign = 1.0 if direction in ("+", "正") else -1.0
        delta = delta_map.get(axis_key, 0.0) * sign
        if axis_key == "x":
            self.x += delta
        elif axis_key == "y":
            self.y += delta
        elif axis_key == "z":
            self.z += delta
        label = axis_key.upper()
        dir_label = "+" if sign > 0 else "-"
        message = f"Mock：运动平台 Jog {label}{dir_label} → X {self.x:.2f} / Y {self.y:.2f} / Z {self.z:.2f}"
        self._emit_message(message)
        return message

    def move_to(self, x: float, y: float, z: float) -> str:
        self.x, self.y, self.z = x, y, z
        message = f"Mock：运动平台移动到 X {x:.2f} / Y {y:.2f} / Z {z:.2f} mm"
        self._emit_message(message)
        return message

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data.update(
            {
                "port": self.port,
                "baudrate": self.baudrate,
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "speed": self.speed,
                "travel_x": self.travel_x,
                "travel_y": self.travel_y,
                "travel_z": self.travel_z,
            }
        )
        return data
