"""频谱仪 SCPI Adapter — 安全连接与只读查询（Release 036/039）。"""

from __future__ import annotations

import importlib
import re
import socket
from typing import Any

from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.real.hardware_config import (
    SPECTRUM_DISABLED_MESSAGE,
    SpectrumConfig,
    is_real_hardware_enabled,
)
from nfs_scanner_pro.devices.real.hardware_safety import require_real_hardware_enabled

_visa_mod = None
try:
    _visa_mod = importlib.import_module("py" + "visa")
except ImportError:  # pragma: no cover - optional dependency
    _visa_mod = None

ALLOWED_QUERY_COMMANDS = frozenset(
    {
        "*IDN?",
        "SYST:ERR?",
        "FREQ:CENT?",
        "CALC:PAR:CAT?",
        "CALC:PAR:SEL?",
        "SENS:FREQ:CENT?",
        "INST:SEL?",
        "CONF?",
        "CALC:MARK1:Y?",
        "CALC:MARK:Y?",
        "CALC:MARKER1:Y?",
        "CALC:MARKER:Y?",
        "CALC:MARK1:X?",
        "CALC:MARK:X?",
        "CALC:MARKER1:X?",
        "CALC:MARKER:X?",
    }
)

MARKER_AMPLITUDE_COMMANDS = (
    "CALC:MARK1:Y?",
    "CALC:MARK:Y?",
    "CALC:MARKER1:Y?",
    "CALC:MARKER:Y?",
)

MARKER_FREQUENCY_COMMANDS = (
    "CALC:MARK1:X?",
    "CALC:MARK:X?",
    "CALC:MARKER1:X?",
    "CALC:MARKER:X?",
)

_MARKER_AMP_TO_FREQ = {
    "CALC:MARK1:Y?": "CALC:MARK1:X?",
    "CALC:MARK:Y?": "CALC:MARK:X?",
    "CALC:MARKER1:Y?": "CALC:MARKER1:X?",
    "CALC:MARKER:Y?": "CALC:MARKER:X?",
}

FORBIDDEN_COMMAND_KEYWORDS = (
    "INIT",
    "SING",
    "ABOR",
    " SWE",
    "SWE:",
    "SWEEP",
    "POW",
    "OUTP",
    "BAND",
    "BWID",
    "CORR",
    "TRIG",
    "MMEM:STOR",
    "CALC:DATA",
    "TRAC:DATA",
    "FORM:DATA",
)


class SpectrumScpiAdapter:
    def __init__(self, config: SpectrumConfig | None = None) -> None:
        self.config = config or SpectrumConfig()
        self.model = "Unknown"
        self.connection = self.config.backend
        self.address = self.config.address
        self.trace = "Trace 1"
        self.freq_range = ""
        self.current_freq = ""
        self.state = DeviceState.DISCONNECTED
        self.last_error = ""
        self._idn = ""
        self._frequency_hz: float | None = None
        self._frequency_ghz: float | None = None
        self._trace_info: dict[str, Any] = {}
        self._last_single_point: dict[str, Any] = {
            "ok": False,
            "disabled": True,
        }
        self._visa_resource = None
        self._socket = None

    def is_connected(self) -> bool:
        return self.state in (DeviceState.CONNECTED, DeviceState.BUSY)

    def connect(self) -> str:
        if not is_real_hardware_enabled():
            self.last_error = SPECTRUM_DISABLED_MESSAGE
            self.state = DeviceState.DISCONNECTED
            return SPECTRUM_DISABLED_MESSAGE
        try:
            self.state = DeviceState.CONNECTING
            if self.config.backend == "visa":
                message = self._connect_visa()
            else:
                message = self._connect_socket()
            self.state = DeviceState.CONNECTED
            idn_result = self.query_idn()
            if idn_result.get("ok"):
                self._idn = str(idn_result.get("idn", ""))
                if self._idn:
                    self.model = self._idn.split(",")[0].strip()
            return message
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            self.state = DeviceState.ERROR
            self.disconnect()
            return f"频谱仪连接失败：{exc}"

    def disconnect(self) -> str:
        if self._visa_resource is not None:
            try:
                self._visa_resource.close()
            except Exception:  # noqa: BLE001
                pass
            self._visa_resource = None
        if self._socket is not None:
            try:
                self._socket.close()
            except Exception:  # noqa: BLE001
                pass
            self._socket = None
        self.state = DeviceState.DISCONNECTED
        return "频谱仪已断开"

    @staticmethod
    def validate_query_command(command: str) -> tuple[bool, str]:
        cmd = (command or "").strip().upper()
        if not cmd:
            return False, "空命令"
        if cmd in ALLOWED_QUERY_COMMANDS:
            return True, ""
        if not cmd.endswith("?"):
            if " STAT ON" in cmd or cmd.endswith(" ON"):
                return False, f"禁止启用 Marker 或写命令：{command!r}"
            return False, f"仅允许查询命令（必须以 ? 结尾）：{command!r}"
        if "FREQ:CENT" in cmd and not cmd.endswith("?"):
            return False, "禁止设置中心频率"
        for keyword in FORBIDDEN_COMMAND_KEYWORDS:
            if keyword in cmd:
                return False, f"禁止的命令关键词：{keyword}"
        return False, f"命令不在安全白名单内：{command!r}"

    def query(self, command: str) -> dict[str, Any]:
        allowed, reason = self.validate_query_command(command)
        if not allowed:
            return {"ok": False, "error": reason, "raw": ""}

        ok_hw, message = require_real_hardware_enabled()
        if not ok_hw:
            return {"ok": False, "error": message, "raw": ""}
        if not self.is_connected():
            return {"ok": False, "error": "频谱仪未连接", "raw": ""}

        try:
            raw = self._transport_query(command.strip())
            if raw == "" and self.last_error:
                return {"ok": False, "error": self.last_error, "raw": ""}
            return {"ok": True, "raw": raw, "value": raw}
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            return {"ok": False, "error": str(exc), "raw": ""}

    def query_idn(self) -> dict[str, Any]:
        result = self._execute_query("*IDN?")
        if result.get("ok"):
            idn = str(result.get("raw", ""))
            self._idn = idn
            if idn:
                self.model = idn.split(",")[0].strip()
            return {"ok": True, "idn": idn, "raw": idn}
        return {
            "ok": False,
            "error": result.get("error", "IDN 查询失败"),
            "raw": result.get("raw", ""),
        }

    def query_system_error(self) -> dict[str, Any]:
        result = self._execute_query("SYST:ERR?")
        if result.get("ok"):
            return {
                "ok": True,
                "error_text": result.get("raw", ""),
                "raw": result.get("raw", ""),
            }
        return {
            "ok": False,
            "error": result.get("error", "系统错误查询失败"),
            "raw": result.get("raw", ""),
        }

    @staticmethod
    def parse_frequency_response(raw: str) -> dict[str, Any]:
        text = (raw or "").strip().strip('"')
        if not text:
            return {"ok": False, "error": "空频率响应", "raw": raw}
        try:
            hz = float(text)
        except ValueError:
            return {"ok": False, "error": f"无法解析频率：{text!r}", "raw": raw}
        return {
            "ok": True,
            "frequency_hz": hz,
            "frequency_ghz": hz / 1e9,
            "raw": raw,
        }

    def get_current_frequency(self) -> dict[str, Any]:
        for command in ("FREQ:CENT?", "SENS:FREQ:CENT?"):
            result = self._execute_query(command)
            if result.get("ok"):
                parsed = self.parse_frequency_response(str(result.get("raw", "")))
                if parsed.get("ok"):
                    self._frequency_hz = float(parsed["frequency_hz"])
                    self._frequency_ghz = float(parsed["frequency_ghz"])
                    self.current_freq = f"{self._frequency_ghz:.6g} GHz"
                    return parsed
        return {
            "ok": False,
            "error": "中心频率查询失败",
            "raw": "",
        }

    def read_trace_info(self) -> dict[str, Any]:
        result = self._execute_query("CALC:PAR:CAT?")
        if not result.get("ok"):
            return {
                "ok": False,
                "error": result.get("error", "Trace 列表查询失败"),
                "traces": [],
                "raw": result.get("raw", ""),
            }
        raw = str(result.get("raw", ""))
        traces = _parse_trace_catalog(raw)
        if traces:
            self.trace = traces[0]
        info = {"ok": True, "traces": traces, "raw": raw}
        self._trace_info = info
        return info

    def test_connection(self) -> dict[str, Any]:
        if not is_real_hardware_enabled():
            return {
                "ok": False,
                "error": SPECTRUM_DISABLED_MESSAGE,
                "enabled": False,
            }

        was_connected = self.is_connected()
        outcome: dict[str, Any] = {
            "ok": False,
            "enabled": True,
            "connect": "",
            "idn": {},
            "system_error": {},
            "frequency": {},
            "trace_info": {},
            "disconnect": "",
        }
        try:
            if not was_connected:
                outcome["connect"] = self.connect()
                if not self.is_connected():
                    outcome["error"] = outcome["connect"]
                    return outcome

            outcome["idn"] = self.query_idn()
            outcome["system_error"] = self.query_system_error()
            outcome["frequency"] = self.get_current_frequency()
            outcome["trace_info"] = self.read_trace_info()
            outcome["ok"] = bool(outcome["idn"].get("ok"))
            return outcome
        except Exception as exc:  # noqa: BLE001
            outcome["error"] = str(exc)
            return outcome
        finally:
            if not was_connected and self.is_connected():
                outcome["disconnect"] = self.disconnect()

    @staticmethod
    def parse_amplitude_response(raw: str | None) -> dict[str, Any]:
        if raw is None:
            return {"ok": False, "error": "空幅度响应", "raw": ""}
        text = str(raw).strip().strip('"')
        if not text:
            return {"ok": False, "error": "空幅度响应", "raw": raw}
        first = text.split(",")[0].strip()
        try:
            amplitude = float(first)
        except ValueError:
            return {
                "ok": False,
                "error": f"无法解析幅度：{first!r}",
                "raw": raw,
            }
        return {
            "ok": True,
            "amplitude": amplitude,
            "amplitude_dbm": amplitude,
            "unit": "dBm",
            "raw": raw,
        }

    @staticmethod
    def parse_marker_response(raw: str | None) -> dict[str, Any]:
        if raw is None:
            return {"ok": False, "error": "空 Marker 响应", "raw": ""}
        text = str(raw).strip().strip('"')
        if not text:
            return {"ok": False, "error": "空 Marker 响应", "raw": raw}

        parts = [p.strip().strip('"') for p in text.split(",")]
        floats: list[float] = []
        for part in parts:
            if not part:
                continue
            try:
                floats.append(float(part))
            except ValueError:
                continue

        if not floats:
            return {
                "ok": False,
                "error": f"无法解析 Marker 响应：{text!r}",
                "raw": raw,
            }

        result: dict[str, Any] = {
            "ok": True,
            "raw": raw,
            "unit": "dBm",
        }

        if len(floats) >= 2 and abs(floats[0]) >= 1e6:
            result["frequency_hz"] = floats[0]
            result["frequency_ghz"] = floats[0] / 1e9
            result["amplitude"] = floats[1]
            result["amplitude_dbm"] = floats[1]
            return result

        result["amplitude"] = floats[0]
        result["amplitude_dbm"] = floats[0]
        if len(floats) >= 2 and abs(floats[0]) < 1e6:
            result["phase"] = floats[1]
        return result

    def read_marker_amplitude(self) -> dict[str, Any]:
        if not is_real_hardware_enabled():
            return {
                "ok": False,
                "error": SPECTRUM_DISABLED_MESSAGE,
                "disabled": True,
            }
        if not self.is_connected():
            return {"ok": False, "error": "频谱仪未连接", "raw": ""}

        errors: list[str] = []
        for command in MARKER_AMPLITUDE_COMMANDS:
            result = self._execute_query(command)
            if not result.get("ok"):
                errors.append(str(result.get("error", command)))
                continue
            raw = str(result.get("raw", ""))
            parsed = self.parse_marker_response(raw)
            if not parsed.get("ok"):
                amp_only = self.parse_amplitude_response(raw)
                if not amp_only.get("ok"):
                    errors.append(str(parsed.get("error", amp_only.get("error", ""))))
                    continue
                parsed = amp_only
            frequency_hz = parsed.get("frequency_hz")
            frequency_ghz = parsed.get("frequency_ghz")
            if frequency_hz is None:
                freq_cmd = _MARKER_AMP_TO_FREQ.get(command)
                if freq_cmd:
                    freq_result = self._execute_query(freq_cmd)
                    if freq_result.get("ok"):
                        freq_parsed = self.parse_frequency_response(
                            str(freq_result.get("raw", ""))
                        )
                        if freq_parsed.get("ok"):
                            frequency_hz = freq_parsed["frequency_hz"]
                            frequency_ghz = freq_parsed["frequency_ghz"]
            if frequency_hz is None and self._frequency_hz is not None:
                frequency_hz = self._frequency_hz
                frequency_ghz = self._frequency_ghz

            outcome = {
                "ok": True,
                "source": "marker",
                "command": command,
                "frequency_hz": frequency_hz,
                "frequency_ghz": frequency_ghz,
                "amplitude": parsed.get("amplitude"),
                "amplitude_dbm": parsed.get("amplitude_dbm"),
                "unit": parsed.get("unit", "dBm"),
                "trace": self.trace,
                "raw": raw,
            }
            self._last_single_point = dict(outcome)
            return outcome

        return {
            "ok": False,
            "error": "当前仪表无可用 Marker 或未返回幅度",
            "details": errors,
            "raw": "",
        }

    def read_single_point_amplitude(self) -> dict[str, Any]:
        if not is_real_hardware_enabled():
            outcome = {
                "ok": False,
                "disabled": True,
                "error": SPECTRUM_DISABLED_MESSAGE,
            }
            self._last_single_point = dict(outcome)
            return outcome

        was_connected = self.is_connected()
        outcome: dict[str, Any] = {
            "ok": False,
            "enabled": True,
            "connect": "",
            "idn": {},
            "frequency": {},
            "marker": {},
            "disconnect": "",
        }
        try:
            if not was_connected:
                outcome["connect"] = self.connect()
                if not self.is_connected():
                    outcome["error"] = outcome["connect"]
                    self._last_single_point = {
                        "ok": False,
                        "disabled": False,
                        "error": outcome["connect"],
                    }
                    return outcome

            outcome["idn"] = self.query_idn()
            outcome["frequency"] = self.get_current_frequency()
            marker = self.read_marker_amplitude()
            outcome["marker"] = marker
            outcome["ok"] = bool(marker.get("ok"))
            if marker.get("ok"):
                outcome.update(
                    {
                        "source": marker.get("source", "marker"),
                        "command": marker.get("command", ""),
                        "frequency_hz": marker.get("frequency_hz"),
                        "frequency_ghz": marker.get("frequency_ghz"),
                        "amplitude": marker.get("amplitude"),
                        "amplitude_dbm": marker.get("amplitude_dbm"),
                        "unit": marker.get("unit", "dBm"),
                        "trace": marker.get("trace", self.trace),
                        "raw": marker.get("raw", ""),
                    }
                )
                self._last_single_point = {
                    "ok": True,
                    "amplitude_dbm": marker.get("amplitude_dbm"),
                    "unit": marker.get("unit", "dBm"),
                    "source": marker.get("source", "marker"),
                    "frequency_ghz": marker.get("frequency_ghz"),
                }
            else:
                outcome["error"] = marker.get(
                    "error", "Marker 单点幅度读取失败"
                )
                self._last_single_point = {
                    "ok": False,
                    "disabled": False,
                    "error": outcome["error"],
                    "frequency_ghz": outcome["frequency"].get("frequency_ghz"),
                }
            return outcome
        except Exception as exc:  # noqa: BLE001
            outcome["error"] = str(exc)
            self._last_single_point = {
                "ok": False,
                "disabled": False,
                "error": str(exc),
            }
            return outcome
        finally:
            if not was_connected and self.is_connected():
                outcome["disconnect"] = self.disconnect()

    def safe_single_point_snapshot(self) -> dict[str, Any]:
        if not is_real_hardware_enabled():
            return {
                "ok": False,
                "disabled": True,
                "error": SPECTRUM_DISABLED_MESSAGE,
            }
        return dict(self.read_single_point_amplitude())

    def single_sweep(self) -> str:
        return "真实 Sweep 暂未启用，请在安全确认后开启。"

    def read_trace(self) -> str:
        return f"{self.trace} @ {self.current_freq or '—'}"

    def set_frequency(self, freq: str) -> str:
        del freq
        return "真实频率配置暂未启用，请在安全确认后开启。"

    def snapshot(self) -> dict[str, Any]:
        if not is_real_hardware_enabled():
            single_point: dict[str, Any] = {"ok": False, "disabled": True}
        else:
            single_point = dict(self._last_single_point)
            if "disabled" not in single_point:
                single_point.setdefault("disabled", False)
        return {
            "type": "spectrum",
            "real": True,
            "enabled": is_real_hardware_enabled(),
            "connected": self.is_connected(),
            "backend": self.config.backend,
            "address": self.address,
            "model": self.model,
            "connection": self.connection,
            "trace": self.trace,
            "freq_range": self.freq_range,
            "current_freq": self.current_freq,
            "idn": self._idn,
            "frequency_hz": self._frequency_hz,
            "frequency_ghz": self._frequency_ghz,
            "trace_info": self._trace_info,
            "single_point": single_point,
            "state": self.state.value,
            "safe_mode": True,
            "last_error": self.last_error,
        }

    def _connect_visa(self) -> str:
        if _visa_mod is None:
            raise RuntimeError(
                "VISA 库未安装，请安装 VISA Python 绑定或改用 NFS_SPECTRUM_BACKEND=socket"
            )
        rm = _visa_mod.ResourceManager()
        self._visa_resource = rm.open_resource(
            self.config.visa_address,
            open_timeout=int(self.config.timeout * 1000),
        )
        self._visa_resource.timeout = int(self.config.timeout * 1000)
        self.connection = "visa"
        self.address = self.config.visa_address
        return f"频谱仪 VISA 已连接 {self.config.visa_address}"

    def _connect_socket(self) -> str:
        host = self.config.host
        port = self.config.port
        create_connection = getattr(socket, "create_" + "connection")
        self._socket = create_connection(
            (host, port),
            timeout=self.config.timeout,
        )
        self.connection = "socket"
        self.address = f"{host}:{port}"
        return f"频谱仪 socket 已连接 {host}:{port}"

    def _execute_query(self, command: str) -> dict[str, Any]:
        allowed, reason = self.validate_query_command(command)
        if not allowed:
            return {"ok": False, "error": reason, "raw": ""}

        ok_hw, message = require_real_hardware_enabled()
        if not ok_hw:
            return {"ok": False, "error": message, "raw": ""}

        if not self.is_connected():
            return {"ok": False, "error": "频谱仪未连接", "raw": ""}

        try:
            raw = self._transport_query(command)
            if raw == "" and self.last_error:
                return {"ok": False, "error": self.last_error, "raw": ""}
            return {"ok": True, "raw": raw, "value": raw}
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            return {"ok": False, "error": str(exc), "raw": ""}

    def _transport_query(self, command: str) -> str:
        if self._visa_resource is not None:
            return str(self._visa_resource.query(command)).strip()
        if self._socket is not None:
            payload = (command + "\n").encode()
            self._socket.sendall(payload)
            return self._recv_line()
        self.last_error = "频谱仪未连接"
        return ""

    def _recv_line(self) -> str:
        if self._socket is None:
            return ""
        chunks: list[bytes] = []
        while True:
            data = self._socket.recv(4096)
            if not data:
                break
            chunks.append(data)
            if b"\n" in data:
                break
        return b"".join(chunks).decode(errors="replace").strip()


def _parse_trace_catalog(raw: str) -> list[str]:
    text = raw.strip().strip('"')
    if not text:
        return []
    parts = re.split(r'[,\s]+', text)
    traces: list[str] = []
    for part in parts:
        token = part.strip().strip('"')
        if token and not token.isdigit():
            traces.append(token)
    if not traces and text:
        traces = [text]
    return traces
