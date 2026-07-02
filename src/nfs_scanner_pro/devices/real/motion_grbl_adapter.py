"""GRBL 运动平台 Adapter — 安全连接、位置读取与手动点动（Release 037/038）。"""

from __future__ import annotations

import time
from typing import Any

from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.real.hardware_config import (
    MotionConfig,
    MotionSafetyConfig,
    is_real_hardware_enabled,
    is_real_motion_estop_enabled,
    is_real_motion_home_enabled,
    is_real_motion_jog_enabled,
    is_real_motion_move_enabled,
    load_motion_safety_config,
)
from nfs_scanner_pro.devices.real.hardware_safety import (
    EMERGENCY_STOP_BLOCKED_MESSAGE,
    ESTOP_DISABLED_MESSAGE,
    HOME_DISABLED_MESSAGE,
    MOTION_BLOCKED_MESSAGE,
    MOTION_DISABLED_MESSAGE,
    MOVE_DISABLED_MESSAGE,
    block_jog_command,
    block_motion_command,
    require_real_hardware_enabled,
    require_real_motion_estop_enabled,
    require_real_motion_home_enabled,
    require_real_motion_jog_enabled,
    require_real_motion_move_enabled,
)
from nfs_scanner_pro.devices.real.transports import BaseTransport

try:
    import importlib

    _serial_mod = importlib.import_module("serial")
except ImportError:  # pragma: no cover - optional dependency
    _serial_mod = None

_GRBL_STARTUP_WAIT_S = 0.15
_JOG_COMMAND_PREFIX = "$J=G91 G21 "
_VALID_AXES = frozenset({"x", "y", "z"})
_VALID_DIRECTIONS = frozenset({"+", "-"})


class MotionGrblAdapter:
    def __init__(
        self,
        config: MotionConfig | None = None,
        safety: MotionSafetyConfig | None = None,
    ) -> None:
        self.config = config or MotionConfig()
        self.safety = safety or load_motion_safety_config()
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
        self._last_command = ""
        self._last_response = ""
        self._serial = None
        self._transport: BaseTransport | None = None
        self._last_status: dict[str, Any] = {}

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
                status = self.query_status()
                if isinstance(status, dict) and status.get("ok"):
                    return message
                return message
            self.state = DeviceState.DISCONNECTED
            return message
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
        if self._transport is not None:
            message = self._transport.disconnect()
            self.state = DeviceState.DISCONNECTED
            self.grbl_state = ""
            return message
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
        if self._transport is not None:
            if not self._transport.is_connected():
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
            raw = self._transport.query("?")
            parsed = self.parse_grbl_status_line(raw)
            if parsed.get("ok"):
                self.grbl_state = str(parsed.get("state", ""))
                self.x = float(parsed.get("x", self.x))
                self.y = float(parsed.get("y", self.y))
                self.z = float(parsed.get("z", self.z))
                self.position_source = str(parsed.get("source", ""))
                self.state = DeviceState.CONNECTED
            self._last_status = parsed
            return parsed
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
            if self.is_connected():
                return {
                    "ok": False,
                    "x": self.x,
                    "y": self.y,
                    "z": self.z,
                    "source": self.position_source,
                    "state": self.grbl_state,
                    "error": status.get("error", "未收到运动平台状态"),
                }
            return self._position_from_state(
                ok=bool(self.x or self.y or self.z),
                error=status.get("error", "未收到运动平台状态"),
            )
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

    def build_jog_command(
        self,
        axis: str,
        direction: str,
        step_mm: float,
        *,
        feed_mm_min: float | None = None,
    ) -> str:
        axis_key = (axis or "").strip().lower()
        if axis_key not in _VALID_AXES:
            raise ValueError(f"非法轴：{axis!r}")
        if direction not in _VALID_DIRECTIONS:
            raise ValueError(f"非法方向：{direction!r}")
        if step_mm <= 0:
            raise ValueError("步长必须大于 0")

        delta = step_mm if direction == "+" else -step_mm
        letter = axis_key.upper()
        feed = feed_mm_min if feed_mm_min is not None else self.safety.jog_feed_mm_min
        return f"{_JOG_COMMAND_PREFIX}{letter}{delta:.3f} F{int(feed)}"

    def validate_jog(
        self,
        axis: str,
        direction: str,
        step_mm: float,
        current_position: dict[str, float],
    ) -> dict[str, Any]:
        axis_key = (axis or "").strip().lower()
        if axis_key not in _VALID_AXES:
            return {
                "ok": False,
                "reason": f"非法轴：{axis!r}",
                "target_position": None,
            }
        if direction not in _VALID_DIRECTIONS:
            return {
                "ok": False,
                "reason": f"非法方向：{direction!r}",
                "target_position": None,
            }
        try:
            step = float(step_mm)
        except (TypeError, ValueError):
            return {
                "ok": False,
                "reason": "步长无效",
                "target_position": None,
            }
        if step <= 0:
            return {
                "ok": False,
                "reason": "步长必须大于 0",
                "target_position": None,
            }
        if step > self.safety.max_jog_step_mm:
            return {
                "ok": False,
                "reason": (
                    f"步长 {step:.3f} mm 超过最大允许 "
                    f"{self.safety.max_jog_step_mm:.3f} mm"
                ),
                "target_position": None,
            }

        try:
            pos = {
                "x": float(current_position["x"]),
                "y": float(current_position["y"]),
                "z": float(current_position["z"]),
            }
        except (KeyError, TypeError, ValueError):
            return {
                "ok": False,
                "reason": "当前位置无效，禁止点动",
                "target_position": None,
            }

        delta = step if direction == "+" else -step
        target = dict(pos)
        target[axis_key] = pos[axis_key] + delta

        limit_reason = _soft_limit_reason(target, self.safety)
        if limit_reason:
            return {
                "ok": False,
                "reason": limit_reason,
                "target_position": target,
            }

        return {"ok": True, "reason": "", "target_position": target}

    def safe_jog(
        self,
        axis: str,
        direction: str,
        step_mm: float,
        *,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        if not self._using_fake_transport():
            ok_jog, jog_message = require_real_motion_jog_enabled()
            if not ok_jog:
                return block_jog_command(jog_message)
        elif self._transport and not self._transport.is_connected():
            self._transport.connect()

        before = self._read_position_for_jog(dry_run=dry_run or self._using_fake_transport())
        if not before.get("ok"):
            return {
                "ok": False,
                "blocked": False,
                "error": before.get("error", "无法读取当前位置，禁止点动"),
            }

        current = {"x": before["x"], "y": before["y"], "z": before["z"]}
        validation = self.validate_jog(axis, direction, step_mm, current)
        if not validation.get("ok"):
            return {
                "ok": False,
                "blocked": False,
                "error": validation.get("reason", "点动校验失败"),
                "target_position": validation.get("target_position"),
            }

        try:
            command = self.build_jog_command(axis, direction, float(step_mm))
        except ValueError as exc:
            return {"ok": False, "blocked": False, "error": str(exc)}

        target = validation["target_position"]
        result: dict[str, Any] = {
            "ok": True,
            "dry_run": dry_run,
            "axis": (axis or "").strip().lower(),
            "direction": direction,
            "step_mm": float(step_mm),
            "command": command,
            "position_before": current,
            "target_position": target,
            "position_after": dict(current),
        }

        if dry_run:
            result["message"] = "dry-run：未发送点动命令"
            return result

        if self._transport is not None:
            self._transport.write(f"{command}\n")
            self._transport.query("?")
            after = self.refresh_position()
            if after.get("ok"):
                result["position_after"] = {
                    "x": after["x"],
                    "y": after["y"],
                    "z": after["z"],
                }
            result["fake"] = self._using_fake_transport()
            result["message"] = "点动完成（transport）"
            return result

        if not self.is_connected():
            return {
                "ok": False,
                "blocked": False,
                "error": "运动平台未连接，无法点动",
                "command": command,
                "target_position": target,
            }

        if self._serial is None:
            return {
                "ok": False,
                "blocked": False,
                "error": "串口未打开，无法点动",
                "command": command,
                "target_position": target,
            }

        try:
            self._write_jog_command(command)
            self._read_jog_response()
            after = self.refresh_position()
            if after.get("ok"):
                result["position_after"] = {
                    "x": after["x"],
                    "y": after["y"],
                    "z": after["z"],
                }
            else:
                result["position_after"] = dict(current)
                result["warning"] = after.get("error", "点动后未能读取位置")
            result["message"] = "点动完成"
            return result
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            return {
                "ok": False,
                "blocked": False,
                "error": f"点动失败：{exc}",
                "command": command,
                "target_position": target,
                "position_before": current,
            }

    def jog(self, axis: str, direction: str, step_mm: float | None = None) -> dict[str, Any]:
        step = self.safety.default_jog_step_mm if step_mm is None else step_mm
        if not is_real_motion_jog_enabled():
            return block_jog_command()
        return self.safe_jog(axis, direction, step, dry_run=False)

    def build_move_command(
        self,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
        *,
        feed: float | None = None,
    ) -> str:
        parts = ["G90", "G21", "G1"]
        coords: list[str] = []
        if x is not None:
            coords.append(f"X{float(x):.3f}")
        if y is not None:
            coords.append(f"Y{float(y):.3f}")
        if z is not None:
            coords.append(f"Z{float(z):.3f}")
        if not coords:
            raise ValueError("至少需要一个坐标")
        feed_val = feed if feed is not None else self.safety.jog_feed_mm_min
        return " ".join(parts + coords + [f"F{int(feed_val)}"])

    def validate_move_target(
        self,
        x: float | None,
        y: float | None,
        z: float | None,
    ) -> dict[str, Any]:
        target: dict[str, float] = {"x": self.x, "y": self.y, "z": self.z}
        if x is not None:
            target["x"] = float(x)
        if y is not None:
            target["y"] = float(y)
        if z is not None:
            target["z"] = float(z)
        if x is None and y is None and z is None:
            return {"ok": False, "reason": "至少需要一个目标坐标", "target": target}
        reason = _soft_limit_reason(target, self.safety)
        if reason:
            return {"ok": False, "reason": reason, "target": target}
        return {"ok": True, "reason": "", "target": target}

    def move_to(
        self,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
        *,
        feed: float | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        if dry_run:
            validation = self.validate_move_target(x, y, z)
            if not validation.get("ok"):
                return {
                    "ok": False,
                    "blocked": False,
                    "error": validation.get("reason", "目标校验失败"),
                }
            try:
                command = self.build_move_command(x, y, z, feed=feed)
            except ValueError as exc:
                return {"ok": False, "error": str(exc)}
            return {
                "ok": True,
                "dry_run": True,
                "command": command,
                "target": validation["target"],
                "message": "dry-run：未发送 move_to 命令",
            }

        if self._using_fake_transport():
            validation = self.validate_move_target(x, y, z)
            if not validation.get("ok"):
                return {
                    "ok": False,
                    "blocked": False,
                    "error": validation.get("reason", "目标校验失败"),
                }
            command = self.build_move_command(x, y, z, feed=feed)
            if self._transport and not self._transport.is_connected():
                self._transport.connect()
            if self._transport:
                self._transport.write(f"{command}\n")
            return {
                "ok": True,
                "fake": True,
                "command": command,
                "target": validation["target"],
                "message": "fake move_to 完成",
            }

        return block_motion_command("move_to")

    def home(self, *, dry_run: bool = False) -> dict[str, Any]:
        command = "$H"
        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "command": command,
                "message": "dry-run：未发送 home 命令",
            }
        if self._using_fake_transport():
            if self._transport and not self._transport.is_connected():
                self._transport.connect()
            if self._transport:
                self._transport.write(f"{command}\n")
            return {
                "ok": True,
                "fake": True,
                "command": command,
                "message": "fake home 完成",
            }
        return block_motion_command("home")

    def emergency_stop(self, *, dry_run: bool = False) -> dict[str, Any]:
        command = "!"
        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "command": command,
                "message": "dry-run：未发送急停",
            }
        if self._using_fake_transport():
            if self._transport:
                self._transport.write(command)
            return {
                "ok": True,
                "fake": True,
                "command": command,
                "message": "fake 急停完成",
            }
        ok_estop, estop_message = require_real_motion_estop_enabled()
        if not ok_estop:
            return {
                "ok": False,
                "blocked": True,
                "message": estop_message or EMERGENCY_STOP_BLOCKED_MESSAGE,
            }
        return {"ok": False, "blocked": True, "message": ESTOP_DISABLED_MESSAGE}

    def emergency_stop_blocked(self) -> dict[str, Any]:
        return {
            "ok": False,
            "blocked": True,
            "message": EMERGENCY_STOP_BLOCKED_MESSAGE,
        }

    def stop(self) -> dict[str, Any]:
        return self.emergency_stop_blocked()

    def snapshot(self) -> dict[str, Any]:
        from nfs_scanner_pro.devices.real.hardware_config import (
            build_adapter_snapshot_common,
            get_motion_config,
            is_real_hardware_enabled,
            is_real_motion_estop_enabled,
            is_real_motion_home_enabled,
            is_real_motion_jog_enabled,
            is_real_motion_move_enabled,
        )

        common = build_adapter_snapshot_common(
            enabled=is_real_hardware_enabled(),
            connected=self.is_connected(),
            fake=self._using_fake_transport(),
            config=get_motion_config(),
            last_error=self.last_error,
            last_command=self._last_command,
            last_response=str(self._last_status.get("raw", "")),
        )
        return {
            "type": "motion",
            "real": True,
            **common,
            "jog_enabled": is_real_motion_jog_enabled(),
            "move_enabled": is_real_motion_move_enabled(),
            "home_enabled": is_real_motion_home_enabled(),
            "estop_enabled": is_real_motion_estop_enabled(),
            "fake_transport": self._using_fake_transport(),
            "port": self.port,
            "baudrate": self.baudrate,
            "state": self.grbl_state or self.state.value,
            "position": {
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "source": self.position_source,
            },
            "jog_limits": {
                "x_min": self.safety.x_min,
                "x_max": self.safety.x_max,
                "y_min": self.safety.y_min,
                "y_max": self.safety.y_max,
                "z_min": self.safety.z_min,
                "z_max": self.safety.z_max,
                "max_jog_step_mm": self.safety.max_jog_step_mm,
                "default_jog_step_mm": self.safety.default_jog_step_mm,
            },
            "raw_status": self._last_status.get("raw", ""),
        }

    def _read_position_for_jog(self, *, dry_run: bool) -> dict[str, Any]:
        if self.is_connected():
            pos = self.refresh_position()
            if pos.get("ok"):
                return pos
            if dry_run:
                return self._position_from_state(ok=True)
            return pos
        if dry_run:
            return self._position_from_state(ok=True)
        return {
            "ok": False,
            "error": "运动平台未连接，无法读取位置",
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

    def _position_from_state(self, *, ok: bool, error: str = "") -> dict[str, Any]:
        return {
            "ok": ok,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "source": self.position_source,
            "state": self.grbl_state,
            "error": error,
        }

    def _write_jog_command(self, command: str) -> None:
        if not command.startswith(_JOG_COMMAND_PREFIX):
            raise ValueError("仅允许 GRBL 增量点动命令")
        for forbidden in ("G0", "G1", "$H", "G28"):
            if forbidden in command:
                raise ValueError(f"禁止发送命令片段：{forbidden}")
        if self._serial is None:
            raise RuntimeError("串口未打开")
        self._serial.write(f"{command}\n".encode("ascii"))

    def _read_jog_response(self) -> str:
        return self._read_line(timeout_extra=self.timeout)

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


def _soft_limit_reason(target: dict[str, float], safety: MotionSafetyConfig) -> str:
    checks = (
        ("x", safety.x_min, safety.x_max),
        ("y", safety.y_min, safety.y_max),
        ("z", safety.z_min, safety.z_max),
    )
    for axis, low, high in checks:
        value = target[axis]
        if value < low or value > high:
            return (
                f"目标位置 {axis.upper()}={value:.3f} mm 超出软限位 "
                f"[{low:.3f}, {high:.3f}]"
            )
    return ""
