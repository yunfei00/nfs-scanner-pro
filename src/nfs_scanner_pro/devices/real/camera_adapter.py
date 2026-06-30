"""相机 Adapter — 仅枚举与信息查询（Release 036）。"""

from __future__ import annotations

from typing import Any

from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.real.hardware_config import CameraConfig
from nfs_scanner_pro.devices.real.hardware_safety import require_real_hardware_enabled

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

    def is_connected(self) -> bool:
        return self.state in (DeviceState.CONNECTED, DeviceState.BUSY)

    def connect(self) -> str:
        ok, message = require_real_hardware_enabled()
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
        self.state = DeviceState.DISCONNECTED
        self.status_label = "未连接"
        return "相机已断开"

    def enumerate_devices(self) -> list[str]:
        ok, message = require_real_hardware_enabled()
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

    def capture(self) -> str:
        return "真实拍照暂未启用，请在安全确认后开启。"

    def refresh_preview(self) -> str:
        return "真实预览暂未启用，请在安全确认后开启。"

    def open_settings(self) -> str:
        return "相机设置暂未启用。"

    def status_text(self) -> str:
        return self.status_label

    def snapshot(self) -> dict[str, Any]:
        return {
            "interface": self.interface,
            "resolution": self.resolution,
            "status": self.status_label,
            "devices": list(self._devices),
            "state": self.state.value,
            "last_error": self.last_error,
        }
