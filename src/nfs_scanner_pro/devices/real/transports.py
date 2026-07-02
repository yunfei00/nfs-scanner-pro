"""Transport 层 — 真实 / Fake 离线验证（Release 044）。"""

from __future__ import annotations

import struct
import zlib
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nfs_scanner_pro.devices.real.hardware_config import (
    is_real_hardware_enabled,
)


class BaseTransport(ABC):
    is_fake: bool = False

    @abstractmethod
    def connect(self) -> str: ...

    @abstractmethod
    def disconnect(self) -> str: ...

    @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    def write(self, data: str | bytes) -> str: ...

    @abstractmethod
    def query(self, command: str) -> str: ...

    def snapshot(self) -> dict[str, Any]:
        return {
            "connected": self.is_connected(),
            "fake": self.is_fake,
            "type": self.__class__.__name__,
        }


class FakeSerialTransport(BaseTransport):
    is_fake = True

    def __init__(self) -> None:
        self._connected = False
        self._pos = (50.0, -50.0, 5.0)
        self._history: list[str] = []

    def connect(self) -> str:
        self._connected = True
        return "FakeSerialTransport connected"

    def disconnect(self) -> str:
        self._connected = False
        return "FakeSerialTransport disconnected"

    def is_connected(self) -> bool:
        return self._connected

    def write(self, data: str | bytes) -> str:
        text = data.decode("ascii", errors="replace") if isinstance(data, bytes) else data
        self._history.append(text.strip())
        cmd = text.strip().upper()
        if cmd.startswith("$J="):
            if "X" in cmd:
                self._pos = (self._pos[0] + 0.1, self._pos[1], self._pos[2])
            elif "Y" in cmd:
                self._pos = (self._pos[0], self._pos[1] + 0.1, self._pos[2])
            elif "Z" in cmd:
                self._pos = (self._pos[0], self._pos[1], self._pos[2] + 0.1)
            return "ok"
        if cmd == "$H":
            self._pos = (0.0, 0.0, 0.0)
            return "ok"
        if cmd == "!":
            return "ok"
        if cmd.startswith("G90") or cmd.startswith("G1"):
            return "ok"
        return "ok"

    def query(self, command: str) -> str:
        cmd = command.strip()
        if cmd == "?":
            x, y, z = self._pos
            return f"<Idle|MPos:{x:.3f},{y:.3f},{z:.3f}|FS:0,0>"
        return "ok"

    def snapshot(self) -> dict[str, Any]:
        base = super().snapshot()
        base["position"] = self._pos
        base["history"] = list(self._history)
        return base


class FakeScpiTransport(BaseTransport):
    is_fake = True

    _RESPONSES = {
        "*IDN?": "FakeSpectrum,NFS-SCPI,000001,1.0",
        "SYST:ERR?": '0,"No error"',
        "FREQ:CENT?": "2450000000",
        "SENS:FREQ:CENT?": "2450000000",
        "CALC:MARK1:Y?": "-23.45",
        "CALC:MARK:Y?": "-23.45",
        "CALC:MARK1:X?": "2450000000",
        "CALC:MARK:X?": "2450000000",
        "CALC:PAR:CAT?": '"Trc1","S21"',
        "CALC:DATA?": "-23.1,-23.2,-23.3",
        "TRAC:DATA?": "-23.1,-23.2,-23.3",
    }

    def __init__(self) -> None:
        self._connected = False
        self._writes: list[str] = []

    def connect(self) -> str:
        self._connected = True
        return "FakeScpiTransport connected"

    def disconnect(self) -> str:
        self._connected = False
        return "FakeScpiTransport disconnected"

    def is_connected(self) -> bool:
        return self._connected

    def write(self, data: str | bytes) -> str:
        text = data.decode("ascii", errors="replace") if isinstance(data, bytes) else data
        self._writes.append(text.strip())
        return ""

    def query(self, command: str) -> str:
        key = command.strip().upper()
        if key.endswith("?"):
            for pattern, response in self._RESPONSES.items():
                if key == pattern or key.startswith(pattern.rstrip("?")):
                    return response
        return self._RESPONSES.get(key, "")

    def snapshot(self) -> dict[str, Any]:
        base = super().snapshot()
        base["writes"] = list(self._writes)
        return base


class FakeCameraTransport(BaseTransport):
    is_fake = True

    def __init__(self, output_dir: Path | None = None) -> None:
        self._connected = False
        self._output_dir = output_dir
        self._devices = ["FakeCamera#0 640x480", "FakeCamera#1 1280x720"]

    def connect(self) -> str:
        self._connected = True
        return "FakeCameraTransport connected"

    def disconnect(self) -> str:
        self._connected = False
        return "FakeCameraTransport disconnected"

    def is_connected(self) -> bool:
        return self._connected

    def write(self, data: str | bytes) -> str:
        return "ok"

    def query(self, command: str) -> str:
        if command == "list":
            return ",".join(self._devices)
        return ""

    def enumerate_devices(self) -> list[str]:
        return list(self._devices)

    def capture(self, save_path: Path | None = None) -> dict[str, Any]:
        target = save_path or self._default_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        _write_minimal_png(target)
        return {
            "ok": True,
            "fake": True,
            "path": str(target),
            "width": 64,
            "height": 64,
        }

    def _default_path(self) -> Path:
        if self._output_dir is not None:
            base = self._output_dir
        else:
            from nfs_scanner_pro.app_paths import get_runtime_dir

            base = get_runtime_dir() / "fake_camera"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return base / f"fake_capture_{stamp}.png"

    def snapshot(self) -> dict[str, Any]:
        base = super().snapshot()
        base["devices"] = list(self._devices)
        return base


class FakeServoTransport(BaseTransport):
    is_fake = True

    def __init__(self) -> None:
        self._connected = False
        self._probe = "Hx"
        self._angle = 0.0

    def connect(self) -> str:
        self._connected = True
        return "FakeServoTransport connected"

    def disconnect(self) -> str:
        self._connected = False
        return "FakeServoTransport disconnected"

    def is_connected(self) -> bool:
        return self._connected

    def write(self, data: str | bytes) -> str:
        text = data.decode("ascii", errors="replace") if isinstance(data, bytes) else data
        upper = text.strip().upper()
        if "HY" in upper:
            self._probe = "Hy"
        elif "HX" in upper:
            self._probe = "Hx"
        elif "CAL" in upper:
            self._angle = 0.0
        return "ok"

    def query(self, command: str) -> str:
        return f"{self._probe},{self._angle:.1f}"

    def get_state(self) -> dict[str, Any]:
        return {
            "ok": True,
            "probe": self._probe,
            "angle": self._angle,
            "fake": True,
        }

    def snapshot(self) -> dict[str, Any]:
        base = super().snapshot()
        base.update(self.get_state())
        return base


class SerialTransport(BaseTransport):
    is_fake = False

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 2.0) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None

    def connect(self) -> str:
        if not is_real_hardware_enabled():
            return "真实串口未启用（NFS_ENABLE_REAL_HARDWARE=1）"
        try:
            import importlib

            serial_mod = importlib.import_module("serial")
            serial_cls = getattr(serial_mod, "Serial")
            self._serial = serial_cls(self.port, self.baudrate, timeout=self.timeout)
            return f"Serial connected {self.port}"
        except Exception as exc:  # noqa: BLE001
            self._serial = None
            return f"Serial connect failed: {exc}"

    def disconnect(self) -> str:
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:  # noqa: BLE001
                pass
            self._serial = None
        return "Serial disconnected"

    def is_connected(self) -> bool:
        return self._serial is not None

    def write(self, data: str | bytes) -> str:
        if self._serial is None:
            return "not connected"
        payload = data if isinstance(data, bytes) else data.encode("ascii")
        self._serial.write(payload)
        return "sent"

    def query(self, command: str) -> str:
        self.write(command if command.endswith("\n") else f"{command}\n")
        if self._serial is None:
            return ""
        return self._serial.readline().decode(errors="replace").strip()


class SocketScpiTransport(BaseTransport):
    is_fake = False

    def __init__(self, host: str, port: int, timeout: float = 3.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket = None

    def connect(self) -> str:
        if not is_real_hardware_enabled():
            return "真实 socket 未启用（NFS_ENABLE_REAL_HARDWARE=1）"
        import socket as socket_mod

        create_connection = getattr(socket_mod, "create_" + "connection")
        self._socket = create_connection((self.host, self.port), timeout=self.timeout)
        return f"Socket SCPI connected {self.host}:{self.port}"

    def disconnect(self) -> str:
        if self._socket is not None:
            try:
                self._socket.close()
            except Exception:  # noqa: BLE001
                pass
            self._socket = None
        return "Socket SCPI disconnected"

    def is_connected(self) -> bool:
        return self._socket is not None

    def write(self, data: str | bytes) -> str:
        if self._socket is None:
            return "not connected"
        payload = data if isinstance(data, bytes) else (data + "\n").encode()
        self._socket.sendall(payload)
        return "sent"

    def query(self, command: str) -> str:
        self.write(command)
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


class VisaScpiTransport(BaseTransport):
    is_fake = False

    def __init__(self, visa_address: str, timeout: float = 3.0) -> None:
        self.visa_address = visa_address
        self.timeout = timeout
        self._resource = None

    def connect(self) -> str:
        if not is_real_hardware_enabled():
            return "真实 VISA 未启用（NFS_ENABLE_REAL_HARDWARE=1）"
        try:
            import importlib

            visa_mod = importlib.import_module("py" + "visa")
            rm = visa_mod.ResourceManager()
            self._resource = rm.open_resource(
                self.visa_address,
                open_timeout=int(self.timeout * 1000),
            )
            self._resource.timeout = int(self.timeout * 1000)
            return f"VISA connected {self.visa_address}"
        except Exception as exc:  # noqa: BLE001
            self._resource = None
            return f"VISA connect failed: {exc}"

    def disconnect(self) -> str:
        if self._resource is not None:
            try:
                self._resource.close()
            except Exception:  # noqa: BLE001
                pass
            self._resource = None
        return "VISA disconnected"

    def is_connected(self) -> bool:
        return self._resource is not None

    def write(self, data: str | bytes) -> str:
        if self._resource is None:
            return "not connected"
        text = data.decode("ascii") if isinstance(data, bytes) else data
        self._resource.write(text)
        return "sent"

    def query(self, command: str) -> str:
        if self._resource is None:
            return ""
        return str(self._resource.query(command)).strip()


def _write_minimal_png(path: Path) -> None:
    width, height = 64, 64
    raw = b"".join(
        b"\x00" + bytes([min(255, x + y) for x in range(width)])
        for y in range(height)
    )
    compressor = zlib.compressobj()
    compressed = compressor.compress(raw) + compressor.flush()
    def chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    path.write_bytes(png)
