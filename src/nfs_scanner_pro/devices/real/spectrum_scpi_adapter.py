"""频谱仪 SCPI Adapter — 仅安全查询（Release 036）。"""

from __future__ import annotations

import importlib
import socket
from typing import Any

from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.real.hardware_config import SpectrumConfig
from nfs_scanner_pro.devices.real.hardware_safety import require_real_hardware_enabled

_visa_mod = None
try:
    _visa_mod = importlib.import_module("py" + "visa")
except ImportError:  # pragma: no cover - optional dependency
    _visa_mod = None


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
        self._visa_resource = None
        self._socket = None

    def is_connected(self) -> bool:
        return self.state in (DeviceState.CONNECTED, DeviceState.BUSY)

    def connect(self) -> str:
        ok, message = require_real_hardware_enabled()
        if not ok:
            self.last_error = message
            self.state = DeviceState.DISCONNECTED
            return message
        try:
            self.state = DeviceState.CONNECTING
            if self.config.backend == "visa":
                message = self._connect_visa()
            else:
                message = self._connect_socket()
            self._idn = self.query_idn()
            if self._idn:
                self.model = self._idn.split(",")[0].strip()
            self.current_freq = self.get_current_frequency()
            self.trace = self.read_trace_info()
            self.state = DeviceState.CONNECTED
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

    def test_connection(self) -> str:
        if not self.is_connected():
            return self.connect()
        idn = self.query_idn()
        return f"频谱仪连接正常：{idn or self.model}"

    def query_idn(self) -> str:
        return self._query("*IDN?")

    def get_current_frequency(self) -> str:
        value = self._query("FREQ:CENT?")
        if not value:
            return self.current_freq
        try:
            hz = float(value)
            if hz >= 1e9:
                return f"{hz / 1e9:.6g} GHz"
            if hz >= 1e6:
                return f"{hz / 1e6:.6g} MHz"
            return f"{hz:.6g} Hz"
        except ValueError:
            return value.strip()

    def read_trace_info(self) -> str:
        catalog = self._query("CALC:PAR:CAT?")
        if catalog:
            first = catalog.strip().strip('"').split(",")[0]
            if first:
                return first
        return self.trace

    def single_sweep(self) -> str:
        return "真实 Sweep 暂未启用，请在安全确认后开启。"

    def read_trace(self) -> str:
        return f"{self.trace} @ {self.current_freq or '—'}"

    def set_frequency(self, freq: str) -> str:
        del freq
        return "真实频率配置暂未启用，请在安全确认后开启。"

    def snapshot(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "connection": self.connection,
            "address": self.address,
            "trace": self.trace,
            "freq_range": self.freq_range,
            "current_freq": self.current_freq,
            "idn": self._idn,
            "state": self.state.value,
            "last_error": self.last_error,
        }

    def _connect_visa(self) -> str:
        if _visa_mod is None:
            raise RuntimeError("VISA 库未安装，请安装 VISA Python 绑定或改用 NFS_SPECTRUM_BACKEND=socket")
        rm = _visa_mod.ResourceManager()
        self._visa_resource = rm.open_resource(
            self.config.visa_resource,
            open_timeout=int(self.config.timeout * 1000),
        )
        self._visa_resource.timeout = int(self.config.timeout * 1000)
        self.connection = "VISA"
        self.address = self.config.visa_resource
        return f"频谱仪 VISA 已连接 {self.config.visa_resource}"

    def _connect_socket(self) -> str:
        host, port = self._parse_host_port(self.config.address)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.config.timeout)
        sock.connect((host, port))
        self._socket = sock
        self.connection = "TCP/IP"
        self.address = f"{host}:{port}"
        return f"频谱仪 TCP/IP 已连接 {host}:{port}"

    def _parse_host_port(self, address: str) -> tuple[str, int]:
        text = address.strip()
        if text.startswith("TCPIP"):
            parts = text.split("::")
            host = parts[2] if len(parts) > 2 else "127.0.0.1"
            return host, 5025
        if ":" in text:
            host, port_text = text.rsplit(":", 1)
            return host, int(port_text)
        return text, 5025

    def _query(self, command: str) -> str:
        ok, message = require_real_hardware_enabled()
        if not ok:
            return ""
        if not self.is_connected() and command != "*IDN?":
            return ""
        try:
            if self._visa_resource is not None:
                return str(self._visa_resource.query(command)).strip()
            if self._socket is not None:
                payload = (command + "\n").encode()
                self._socket.sendall(payload)
                return self._recv_line()
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
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
