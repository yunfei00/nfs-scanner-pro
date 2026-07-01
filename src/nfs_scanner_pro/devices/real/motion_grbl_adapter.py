"""GRBL 运动平台 Adapter — 安全连接与位置读取（Release 037）。"""

from __future__ import annotations

import time
from typing import Any

from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.real.hardware_config import MotionConfig, is_real_hardware_enabled
from nfs_scanner_pro.devices.real.hardware_safety import (
    MOTION_DISABLED_MESSAGE,
    block_motion_command,
    require_real_hardware_enabled,
)

try:
    import importlib

    _serial_mod = importlib.import_module("serial")
except ImportError:  # pragma: no cover - optional dependency
    _serial_mod = None

_GRBL_STARTUP_WAIT_S = 0.15


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
        self.grbl_state = ""
        self.position_source = ""
        self.last_error = ""
        self._serial = None
        self._last_status: dict[str, Any] = {}

    def is_connected(self) -> bool:
        return self.state in (DeviceState.CONNECTED, DeviceState.BUSY)

    def connect(self) -> str:
        if not is_real_hardware_enabled():
            self.last_error = MOTION_DISABLED_MESSAGE
            self.state = DeviceState.DISCONNECTED
            return MOTION_DISABLED_MESSAGE
        if _serial_mod is None:
            self.last_error = "pyserial 未安装，请执行 pip install pyserial"
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
            time.sleep(_GRBL_STARTUP_WAIT_S)
            status = self.query_status()
            if isinstance(status, dict) and status.get("ok"):
                self.state = DeviceState.CONNECTED
                return f"运动平台已连接 {self.port} @ {self.baudrate}"
            if isinstance(status, dict) and status.get("error"):
                self.last_error = str(status["error"])
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
        self.grbl_state = ""
        return "运动平台已断开"

    def query_status(self) -> dict[str, Any]:
        ok_enabled, message = require_real_hardware_enabled()
        if not ok_enabled:
            return {
                "ok": False,
                "error": message,
                "raw": "",
                "state": "",
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "source": "",
            }
        if self._serial is None:
            return {
                "ok": False,
                "error": "运动平台未连接",
                "raw": "",
                "state": "",
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "source": "",
            }
        try:
            self._serial.write(b"?")
            raw = self._read_line(timeout_extra=self.timeout)
            parsed = self.parse_grbl_status_line(raw)
            if parsed.get("ok"):
                self.grbl_state = str(parsed.get("state", ""))
                self.x = float(parsed.get("x", self.x))
                self.y = float(parsed.get("y", self.y))
                self.z = float(parsed.get("z", self.z))
                self.position_source = str(parsed.get("source", ""))
                if self.grbl_state.lower() in ("run", "hold", "jog"):
                    self.state = DeviceState.BUSY
                else:
                    self.state = DeviceState.CONNECTED
            else:
                self.last_error = str(parsed.get("error") or "未收到运动平台状态")
            self._last_status = parsed
            return parsed
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            self.state = DeviceState.ERROR
            return {
                "ok": False,
                "error": f"状态查询失败：{exc}",
                "raw": "",
                "state": "",
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "source": "",
            }

    def refresh_position(self) -> dict[str, Any]:
        status = self.query_status()
        if not status.get("ok"):
            return {
                "ok": False,
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "source": self.position_source,
                "state": self.grbl_state,
                "error": status.get("error", "未收到运动平台状态"),
            }
        return {
            "ok": True,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "source": self.position_source or status.get("source", ""),
            "state": self.grbl_state or status.get("state", ""),
        }

    @staticmethod
    def parse_grbl_status_line(line: str) -> dict[str, Any]:
        raw = (line or "").strip()
        result: dict[str, Any] = {
            "state": "",
            "mpos": None,
            "wpos": None,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
            "source": "",
            "raw": raw,
            "ok": False,
            "error": "",
        }
        if not raw.startswith("<") or not raw.endswith(">"):
            result["error"] = raw or "未收到运动平台状态"
            return result

        parts = raw[1:-1].split("|")
        if parts:
            result["state"] = parts[0].strip()

        mpos_coords: tuple[float, float, float] | None = None
        wpos_coords: tuple[float, float, float] | None = None

        for part in parts[1:]:
            token = part.strip()
            if token.startswith("MPos:"):
                mpos_coords = _parse_coord_triplet(token[5:])
            elif token.startswith("WPos:"):
                wpos_coords = _parse_coord_triplet(token[5:])

        if mpos_coords is not None:
            result["mpos"] = mpos_coords
            result["x"], result["y"], result["z"] = mpos_coords
            result["source"] = "MPos"
            result["ok"] = True
        elif wpos_coords is not None:
            result["wpos"] = wpos_coords
            result["x"], result["y"], result["z"] = wpos_coords
            result["source"] = "WPos"
            result["ok"] = True
        else:
            result["error"] = "未收到运动平台状态"

        return result

    def jog(self, axis: str, direction: str) -> dict[str, Any]:
        del axis, direction
        return block_motion_command("jog")

    def move_to(self, x: float, y: float, z: float) -> dict[str, Any]:
        del x, y, z
        return block_motion_command("move_to")

    def home(self) -> dict[str, Any]:
        return block_motion_command("home")

    def stop(self) -> dict[str, Any]:
        return block_motion_command("stop")

    def snapshot(self) -> dict[str, Any]:
        return {
            "type": "motion",
            "real": True,
            "enabled": is_real_hardware_enabled(),
            "connected": self.is_connected(),
            "port": self.port,
            "baudrate": self.baudrate,
            "state": self.grbl_state or self.state.value,
            "position": {
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "source": self.position_source,
            },
            "safe_mode": True,
            "last_error": self.last_error,
            "raw_status": self._last_status.get("raw", ""),
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


def _parse_coord_triplet(text: str) -> tuple[float, float, float] | None:
    parts = [p.strip() for p in text.split(",")]
    if len(parts) < 3:
        return None
    try:
        return float(parts[0]), float(parts[1]), float(parts[2])
    except ValueError:
        return None
