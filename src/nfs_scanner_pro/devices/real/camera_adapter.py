"""相机 Adapter — 枚举 / 采集 / Fake 离线（Release 044）。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from nfs_scanner_pro.app_paths import get_runtime_dir
from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.real.hardware_config import (
    CAMERA_DISABLED_MESSAGE,
    CameraConfig,
    is_real_camera_enabled,
    is_real_hardware_enabled,
)
from nfs_scanner_pro.devices.real.hardware_safety import require_real_camera_enabled
from nfs_scanner_pro.devices.real.transports import BaseTransport, FakeCameraTransport

try:
    import importlib

    _cv2_mod = importlib.import_module("cv2")
except ImportError:  # pragma: no cover - optional dependency
    _cv2_mod = None


class CameraAdapter:
    def __init__(self, config: CameraConfig | None = None) -> None:
        self.config = config or CameraConfig()
        self.interface = "USB3.0"
        self.resolution = "—"
        self.status_label = "未连接"
        self.capture_x = 0.0
        self.capture_y = 0.0
        self.capture_z = 0.0
        self.state = DeviceState.DISCONNECTED
        self.last_error = ""
        self._devices: list[str] = []
        self._transport: BaseTransport | None = None
        self._capture = None

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
                self._devices = self.enumerate_devices()
                self.status_label = f"Fake 相机已连接（{len(self._devices)}）"
            return message
        ok, message = require_real_camera_enabled()
        if not ok:
            self.last_error = message
            self.state = DeviceState.DISCONNECTED
            return message
        try:
            self._devices = self.enumerate_devices()
            if self._devices:
                self.status_label = f"发现 {len(self._devices)} 个相机"
                self.state = DeviceState.CONNECTED
                return self.status_label
            self.status_label = "未发现相机设备"
            self.state = DeviceState.DISCONNECTED
            return self.status_label
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            self.state = DeviceState.ERROR
            return f"相机枚举失败：{exc}"

    def disconnect(self) -> str:
        if self._transport is not None:
            message = self._transport.disconnect()
            self.state = DeviceState.DISCONNECTED
            self.status_label = "未连接"
            return message
        if self._capture is not None:
            try:
                self._capture.release()
            except Exception:  # noqa: BLE001
                pass
            self._capture = None
        self.state = DeviceState.DISCONNECTED
        self.status_label = "未连接"
        return "相机已断开"

    def enumerate_devices(self) -> list[str]:
        if isinstance(self._transport, FakeCameraTransport):
            return self._transport.enumerate_devices()
        ok, message = require_real_camera_enabled()
        if not ok:
            return []
        if _cv2_mod is None:
            self.last_error = "opencv-python 未安装，请 pip install opencv-python"
            return []
        video_capture = getattr(_cv2_mod, "VideoCapture")
        cap_prop_width = getattr(_cv2_mod, "CAP_PROP_FRAME_WIDTH")
        cap_prop_height = getattr(_cv2_mod, "CAP_PROP_FRAME_HEIGHT")
        names: list[str] = []
        for index in range(4):
            capture = video_capture(index)
            try:
                if capture.isOpened():
                    width = int(capture.get(cap_prop_width) or 0)
                    height = int(capture.get(cap_prop_height) or 0)
                    names.append(f"Camera#{index} {width}x{height}")
            finally:
                capture.release()
        self._devices = names
        if names:
            self.resolution = names[0].split(" ", 1)[-1]
        return names

    def capture_image(
        self,
        save_path: Path | str | None = None,
        *,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "message": "dry-run：未拍照",
            }
        if isinstance(self._transport, FakeCameraTransport):
            if not self._transport.is_connected():
                self._transport.connect()
            target = Path(save_path) if save_path else None
            result = self._transport.capture(target)
            self.state = DeviceState.CONNECTED
            return result
        ok, message = require_real_camera_enabled()
        if not ok:
            return {"ok": False, "blocked": True, "error": message}
        if _cv2_mod is None:
            return {"ok": False, "error": "opencv-python 未安装"}
        if not self.is_connected():
            connect_msg = self.connect()
            if not self.is_connected():
                return {"ok": False, "error": connect_msg}
        video_capture = getattr(_cv2_mod, "VideoCapture")
        cap = video_capture(self.config.device_index)
        if not cap.isOpened():
            return {"ok": False, "error": "无法打开相机"}
        try:
            ok_frame, frame = cap.read()
            if not ok_frame:
                return {"ok": False, "error": "采集帧失败"}
            out_dir = Path(os.environ.get("NFS_CAMERA_OUTPUT_DIR", str(get_runtime_dir() / "camera")))
            out_dir.mkdir(parents=True, exist_ok=True)
            target = Path(save_path) if save_path else out_dir / "capture.png"
            imwrite = getattr(_cv2_mod, "imwrite")
            imwrite(str(target), frame)
            return {"ok": True, "path": str(target)}
        finally:
            cap.release()

    def capture(self) -> str:
        result = self.capture_image(dry_run=True)
        return result.get("message", CAMERA_DISABLED_MESSAGE)

    def refresh_preview(self) -> str:
        return "真实预览暂未启用，请在安全确认后开启。"

    def open_settings(self) -> str:
        return "相机设置暂未启用。"

    def status_text(self) -> str:
        return self.status_label

    def snapshot(self) -> dict[str, Any]:
        return {
            "type": "camera",
            "real": True,
            "enabled": is_real_hardware_enabled(),
            "camera_enabled": is_real_camera_enabled(),
            "fake_transport": self._using_fake_transport(),
            "interface": self.interface,
            "resolution": self.resolution,
            "status": self.status_label,
            "devices": list(self._devices),
            "state": self.state.value,
            "last_error": self.last_error,
            "safe_mode": True,
        }
