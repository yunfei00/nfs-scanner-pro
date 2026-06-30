"""舵机 Adapter — 仅读取配置（Release 036）。"""

from __future__ import annotations

from typing import Any

from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.real.hardware_config import ServoConfig
from nfs_scanner_pro.devices.real.hardware_safety import (
    block_servo_motion_command,
    require_real_hardware_enabled,
)


class ServoAdapter:
    def __init__(self, config: ServoConfig | None = None) -> None:
        self.config = config or ServoConfig()
        self.current_probe = self.config.current_probe
        self.hy_status = "待命"
        self.angle = "0.0°"
        self.offset = "X +0.00 / Y +0.00 mm"
        self.calibration = "未连接"
        self.state = DeviceState.DISCONNECTED
        self.last_error = ""

    def is_connected(self) -> bool:
        return self.state in (DeviceState.CONNECTED, DeviceState.BUSY)

    def connect(self) -> str:
        ok, message = require_real_hardware_enabled()
        if not ok:
            self.last_error = message
            self.state = DeviceState.DISCONNECTED
            return message
        self.state = DeviceState.CONNECTED
        self.calibration = "配置已读取（未执行旋转）"
        port = self.config.port or "未配置"
        return f"舵机配置已加载 port={port} probe={self.current_probe}"

    def disconnect(self) -> str:
        self.state = DeviceState.DISCONNECTED
        self.calibration = "未连接"
        return "舵机已断开"

    def switch_to_hx(self) -> str:
        return block_servo_motion_command("switch_to_hx")

    def switch_to_hy(self) -> str:
        return block_servo_motion_command("switch_to_hy")

    def calibrate(self) -> str:
        return block_servo_motion_command("calibrate")

    def apply_offset(self) -> str:
        return block_servo_motion_command("apply_offset")

    def snapshot(self) -> dict[str, Any]:
        return {
            "current_probe": self.current_probe,
            "hy_status": self.hy_status,
            "angle": self.angle,
            "offset": self.offset,
            "calibration": self.calibration,
            "port": self.config.port,
            "state": self.state.value,
            "last_error": self.last_error,
        }
