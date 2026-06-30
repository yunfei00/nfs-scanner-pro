"""GRBL 运动平台 Adapter — 仅安全连接与查询（Release 036）。"""

from __future__ import annotations

from typing import Any

from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.real.hardware_config import MotionConfig
from nfs_scanner_pro.devices.real.hardware_safety import (
    block_motion_command,
    require_real_hardware_enabled,
)

try:
    import importlib

    _serial_mod = importlib.import_module("serial")
except ImportError:  # pragma: no cover - optional dependency
    _serial_mod = None


class MotionGrblAdapter:
    def __init__(self, config: MotionConfig | None = None) -> None:
        self.config = config or MotionConfig()
        self.port = self.config.port
        self.baudrate = self.config.baudrate
        self.timeout = self.config.timeout
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.speed = 1000
        self.state = DeviceState.DISCONNECTED
        self.last_error = ""
        self._serial = None
        self._status_line = ""

    def is_connected(self) -> bool:
        return self.state in (DeviceState.CONNECTED, DeviceState.BUSY)

    def connect(self) -> str:
        ok, message = require_real_hardware_enabled()
        if not ok:
            self.last_error = message
            self.state = DeviceState.DISCONNECTED
            return message
        if _serial_mod is None:
            self.last_error = "pyserial 未安装，请 pip install pyserial"
            self.state = DeviceState.ERROR
            return self.last_error
        try:
            self.state = DeviceState.CONNECTING
            serial_cls = getattr(_serial_mod, "Serial")
            self._serial = serial_cls(
                self.port,
                self.baudrate,
                timeout=self.timeout,
            )
            self._serial.reset_input_buffer()
            self._serial.write(b"\r\n")
            self.query_status()
            self.refresh_position()
            self.state = DeviceState.CONNECTED
            return f"运动平台已连接 {self.port} @ {self.baudrate}"
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            self.state = DeviceState.ERROR
            self._serial = None
            return f"运动平台连接失败：{exc}"

    def disconnect(self) -> str:
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:  # noqa: BLE001
                pass
            self._serial = None
        self.state = DeviceState.DISCONNECTED
        return "运动平台已断开"

    def query_status(self) -> str:
        ok, message = require_real_hardware_enabled()
        if not ok:
            return message
        if self._serial is None:
            return "运动平台未连接"
        try:
            self._serial.write(b"?")
            raw = self._serial.readline().decode(errors="replace").strip()
            self._status_line = raw
            return raw or "GRBL 状态已查询"
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            self.state = DeviceState.ERROR
            return f"状态查询失败：{exc}"

    def refresh_position(self) -> str:
        ok, message = require_real_hardware_enabled()
        if not ok:
            return message
        if self._serial is None:
            return "运动平台未连接"
        try:
            self._serial.write(b"M114\n")
            line = self._read_line(timeout_extra=1.0)
            if line.startswith("ok"):
                line = self._read_line(timeout_extra=1.0)
            self._parse_position_line(line)
            return f"位置 X {self.x:.3f} / Y {self.y:.3f} / Z {self.z:.3f}"
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            return f"位置读取失败：{exc}"

    def jog(self, axis: str, direction: str) -> str:
        del axis, direction
        return block_motion_command("jog")

    def move_to(self, x: float, y: float, z: float) -> str:
        del x, y, z
        return block_motion_command("move_to")

    def home(self) -> str:
        return block_motion_command("home")

    def stop(self) -> str:
        return block_motion_command("stop")

    def snapshot(self) -> dict[str, Any]:
        return {
            "port": self.port,
            "baudrate": self.baudrate,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "speed": self.speed,
            "state": self.state.value,
            "status_line": self._status_line,
            "last_error": self.last_error,
        }

    def _read_line(self, *, timeout_extra: float = 0.0) -> str:
        if self._serial is None:
            return ""
        old_timeout = self._serial.timeout
        if timeout_extra > 0:
            self._serial.timeout = timeout_extra
        try:
            return self._serial.readline().decode(errors="replace").strip()
        finally:
            self._serial.timeout = old_timeout

    def _parse_position_line(self, line: str) -> None:
        if not line:
            return
        parts = line.replace(":", " ").replace("/", " ").split()
        for index, token in enumerate(parts):
            key = token.lower()
            if key in ("x", "y", "z") and index + 1 < len(parts):
                try:
                    value = float(parts[index + 1])
                except ValueError:
                    continue
                if key == "x":
                    self.x = value
                elif key == "y":
                    self.y = value
                elif key == "z":
                    self.z = value
