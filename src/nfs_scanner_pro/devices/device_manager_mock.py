"""设备管理器 Mock — Release 018。"""

from __future__ import annotations

from typing import Any

from nfs_scanner_pro.devices.camera_mock import CameraSystemMock
from nfs_scanner_pro.devices.device_snapshot import build_device_snapshot
from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.device_types import DeviceType, device_type_label
from nfs_scanner_pro.devices.motion_mock import MotionControllerMock
from nfs_scanner_pro.devices.servo_mock import ServoSystemMock
from nfs_scanner_pro.devices.spectrum_mock import SpectrumAnalyzerMock

_manager: DeviceManagerMock | None = None


def get_device_manager() -> DeviceManagerMock:
    global _manager
    if _manager is None:
        _manager = DeviceManagerMock()
    return _manager


class DeviceManagerMock:
    def __init__(self) -> None:
        self.motion = MotionControllerMock()
        self.spectrum = SpectrumAnalyzerMock()
        self.camera = CameraSystemMock()
        self.servo = ServoSystemMock()
        self._devices = {
            DeviceType.MOTION: self.motion,
            DeviceType.SPECTRUM: self.spectrum,
            DeviceType.CAMERA: self.camera,
            DeviceType.SERVO: self.servo,
        }

    def connect_all(self) -> str:
        for device in self._devices.values():
            device.connect()
        message = "Mock：全部设备已连接"
        return message

    def disconnect_all(self) -> str:
        for device in self._devices.values():
            device.disconnect()
        return "Mock：全部设备已断开"

    def get_device(self, device_type: DeviceType | str) -> Any:
        if isinstance(device_type, str):
            device_type = DeviceType(device_type)
        return self._devices[device_type]

    def get_device_status(self) -> list[dict[str, str]]:
        details = {
            DeviceType.MOTION: self.motion.port,
            DeviceType.SPECTRUM: self.spectrum.model,
            DeviceType.CAMERA: self.camera.interface,
            DeviceType.SERVO: "",
        }
        rows: list[dict[str, str]] = []
        for device_type, device in self._devices.items():
            rows.append(
                {
                    "name": device_type_label(device_type),
                    "detail": details[device_type],
                    "status": device.state.chip_status(),
                }
            )
        return rows

    def get_snapshot(self) -> dict[str, Any]:
        return build_device_snapshot(
            self.motion.snapshot(),
            self.spectrum.snapshot(),
            self.camera.snapshot(),
            self.servo.snapshot(),
        )

    def test_all(self) -> str:
        messages = [
            self.motion.connect(),
            self.spectrum.test_connection(),
            self.camera.connect(),
            self.servo.connect(),
        ]
        return messages[-2] if messages else "Mock：设备测试完成"

    def is_all_ready(self) -> bool:
        return all(device.is_connected() for device in self._devices.values())

    def device_tooltips(self) -> dict[str, str]:
        m = self.motion
        return {
            "运动平台": (
                f"运动平台\n端口：{m.port}\n波特率：{m.baudrate}\n"
                f"状态：{m.status_text()}\n"
                f"坐标：X {m.x:.2f} / Y {m.y:.2f} / Z {m.z:.2f}"
            ),
            "频谱仪": (
                f"频谱仪\n型号：{self.spectrum.model}\n状态：{self.spectrum.status_text()}"
            ),
            "相机": (
                f"相机\n接口：{self.camera.interface}\n状态：{self.camera.status_text()}"
            ),
            "舵机系统": f"舵机系统\n状态：{self.servo.status_text()}",
        }

    def sync_mock_data(self) -> None:
        """同步 UI mock_data 模块中的设备常量（供状态栏 meta 等使用）。"""
        from nfs_scanner_pro.ui import mock_data

        mock_data.MOTION_STATE.update(
            {
                "port": self.motion.port,
                "baudrate": self.motion.baudrate,
                "status": self.motion.status_text(),
                "x": self.motion.x,
                "y": self.motion.y,
                "z": self.motion.z,
                "speed": self.motion.speed,
            }
        )
        mock_data.SPECTRUM_STATE.update(
            {
                "model": self.spectrum.model,
                "connection": self.spectrum.connection,
                "address": self.spectrum.address,
                "trace": self.spectrum.trace,
                "freq_range": self.spectrum.freq_range,
                "current_freq": self.spectrum.current_freq,
            }
        )
        mock_data.CAMERA_STATE.update(
            {
                "interface": self.camera.interface,
                "resolution": self.camera.resolution,
                "status": self.camera.status_label,
                "capture_x": self.camera.capture_x,
                "capture_y": self.camera.capture_y,
                "capture_z": self.camera.capture_z,
            }
        )
        mock_data.SERVO_STATE.update(
            {
                "current_probe": self.servo.current_probe,
                "hy_status": self.servo.hy_status,
                "angle": self.servo.angle,
                "offset": self.servo.offset,
                "calibration": self.servo.calibration,
            }
        )
        mock_data.POSITION.update(
            {
                "x": self.motion.x,
                "y": self.motion.y,
                "z": self.motion.z,
            }
        )
        mock_data.DEVICE_STATUS[:] = self.get_device_status()
        mock_data.DEVICE_TOOLTIPS.clear()
        mock_data.DEVICE_TOOLTIPS.update(self.device_tooltips())
