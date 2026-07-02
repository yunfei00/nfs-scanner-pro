"""舵机 / HxHy Adapter — Fake 离线与强安全开关（Release 044）。"""

from __future__ import annotations

import os
from typing import Any

from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.real.hardware_config import (
    SERVO_DISABLED_MESSAGE,
    ServoConfig,
    is_real_hardware_enabled,
    is_real_servo_enabled,
)
from nfs_scanner_pro.devices.real.hardware_safety import require_real_servo_enabled
from nfs_scanner_pro.devices.real.transports import BaseTransport, FakeServoTransport


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
        self._last_command = ""
        self._last_response = ""
        self._transport: BaseTransport | None = None

    def bind_transport(self, transport: BaseTransport | None) -> None:
        self._transport = transport

    def _using_fake_transport(self) -> bool:
        return self._transport is not None and getattr(self._transport, "is_fake", False)

    def is_connected(self) -> bool:
        return self.state in (DeviceState.CONNECTED, DeviceState.BUSY)

    def connect(self) -> str:
        if self._transport is not None:
            message = self._transport.connect()
            if self._transport.is_connected():
                self.state = DeviceState.CONNECTED
                self.calibration = "Fake 舵机已连接"
            return message
        ok, message = require_real_servo_enabled()
        if not ok:
            self.last_error = message
            self.state = DeviceState.DISCONNECTED
            return message
        self.state = DeviceState.CONNECTED
        self.calibration = "配置已读取（未执行旋转）"
        port = self.config.port or "未配置"
        return f"舵机配置已加载 port={port} probe={self.current_probe}"

    def disconnect(self) -> str:
        if self._transport is not None:
            message = self._transport.disconnect()
            self.state = DeviceState.DISCONNECTED
            self.calibration = "未连接"
            return message
        self.state = DeviceState.DISCONNECTED
        self.calibration = "未连接"
        return "舵机已断开"

    def get_state(self) -> dict[str, Any]:
        if isinstance(self._transport, FakeServoTransport):
            if not self._transport.is_connected():
                self._transport.connect()
            state = self._transport.get_state()
            self.current_probe = str(state.get("probe", self.current_probe))
            self.angle = f"{float(state.get('angle', 0.0)):.1f}°"
            return state
        return {
            "ok": self.is_connected(),
            "probe": self.current_probe,
            "angle": self.angle,
            "fake": False,
        }

    def switch_hx(self, *, dry_run: bool = False) -> dict[str, Any]:
        return self._switch_probe("Hx", dry_run=dry_run)

    def switch_hy(self, *, dry_run: bool = False) -> dict[str, Any]:
        return self._switch_probe("Hy", dry_run=dry_run)

    def switch_to_hx(self) -> str:
        result = self.switch_hx(dry_run=True)
        return result.get("message", SERVO_DISABLED_MESSAGE)

    def switch_to_hy(self) -> str:
        result = self.switch_hy(dry_run=True)
        return result.get("message", SERVO_DISABLED_MESSAGE)

    def calibrate(self, *, dry_run: bool = False) -> dict[str, Any]:
        command = "CAL"
        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "command": command,
                "message": "dry-run：未执行校准",
            }
        if self._using_fake_transport() and self._transport:
            if not self._transport.is_connected():
                self._transport.connect()
            self._transport.write(command)
            return {"ok": True, "fake": True, "command": command}
        ok, message = require_real_servo_enabled()
        if not ok:
            return {"ok": False, "blocked": True, "message": message}
        return {"ok": False, "blocked": True, "message": SERVO_DISABLED_MESSAGE}

    def apply_offset(self) -> str:
        return SERVO_DISABLED_MESSAGE

    def _switch_probe(self, probe: str, *, dry_run: bool) -> dict[str, Any]:
        command = f"SWITCH_{probe.upper()}"
        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "command": command,
                "message": f"dry-run：未切换到 {probe}",
            }
        if self._using_fake_transport() and self._transport:
            if not self._transport.is_connected():
                self._transport.connect()
            self._transport.write(command)
            state = self.get_state()
            return {
                "ok": True,
                "fake": True,
                "command": command,
                "probe": state.get("probe", probe),
            }
        ok, message = require_real_servo_enabled()
        if not ok:
            return {"ok": False, "blocked": True, "message": message}
        return {"ok": False, "blocked": True, "message": SERVO_DISABLED_MESSAGE}

    def snapshot(self) -> dict[str, Any]:
        from nfs_scanner_pro.devices.real.hardware_config import (
            build_adapter_snapshot_common,
            get_servo_config,
            is_real_hardware_enabled,
            is_real_servo_enabled,
        )

        common = build_adapter_snapshot_common(
            enabled=is_real_hardware_enabled(),
            connected=self.is_connected(),
            fake=self._using_fake_transport(),
            config=get_servo_config(),
            last_error=self.last_error,
            last_command=self._last_command,
            last_response=self._last_response,
        )
        return {
            "type": "servo",
            "real": True,
            **common,
            "servo_enabled": is_real_servo_enabled(),
            "fake_transport": self._using_fake_transport(),
            "current_probe": self.current_probe,
            "hy_status": self.hy_status,
            "angle": self.angle,
            "offset": self.offset,
            "calibration": self.calibration,
            "port": self.config.port,
            "hx_angle": os.environ.get("NFS_SERVO_HX_ANGLE", str(self.config.hx_angle)),
            "hy_angle": os.environ.get("NFS_SERVO_HY_ANGLE", str(self.config.hy_angle)),
            "state": self.state.value,
        }
