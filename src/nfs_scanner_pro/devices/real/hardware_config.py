"""真实硬件配置 — Release 036 Real Device Bridge。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def is_real_hardware_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_HARDWARE", "").strip() == "1"


@dataclass
class MotionConfig:
    port: str = "COM6"
    baudrate: int = 115200
    timeout: float = 2.0


@dataclass
class SpectrumConfig:
    backend: str = "socket"
    address: str = "192.168.1.10:5025"
    visa_resource: str = "TCPIP0::192.168.1.10::inst0::INSTR"
    timeout: float = 5.0


@dataclass
class CameraConfig:
    backend: str = "opencv"
    device_index: int = 0


@dataclass
class ServoConfig:
    port: str = ""
    baudrate: int = 115200
    timeout: float = 2.0
    current_probe: str = "Hx"


@dataclass
class HardwareConfig:
    motion: MotionConfig = field(default_factory=MotionConfig)
    spectrum: SpectrumConfig = field(default_factory=SpectrumConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    servo: ServoConfig = field(default_factory=ServoConfig)


def load_hardware_config() -> HardwareConfig:
    motion = MotionConfig(
        port=os.environ.get("NFS_MOTION_PORT", "COM6"),
        baudrate=int(os.environ.get("NFS_MOTION_BAUDRATE", "115200")),
        timeout=float(os.environ.get("NFS_MOTION_TIMEOUT", "2.0")),
    )
    spectrum = SpectrumConfig(
        backend=os.environ.get("NFS_SPECTRUM_BACKEND", "socket"),
        address=os.environ.get("NFS_SPECTRUM_ADDRESS", "192.168.1.10:5025"),
        visa_resource=os.environ.get(
            "NFS_SPECTRUM_VISA_RESOURCE",
            "TCPIP0::192.168.1.10::inst0::INSTR",
        ),
        timeout=float(os.environ.get("NFS_SPECTRUM_TIMEOUT", "5.0")),
    )
    camera = CameraConfig(
        backend=os.environ.get("NFS_CAMERA_BACKEND", "opencv"),
        device_index=int(os.environ.get("NFS_CAMERA_INDEX", "0")),
    )
    servo = ServoConfig(
        port=os.environ.get("NFS_SERVO_PORT", ""),
        baudrate=int(os.environ.get("NFS_SERVO_BAUDRATE", "115200")),
        timeout=float(os.environ.get("NFS_SERVO_TIMEOUT", "2.0")),
        current_probe=os.environ.get("NFS_SERVO_PROBE", "Hx"),
    )
    return HardwareConfig(motion=motion, spectrum=spectrum, camera=camera, servo=servo)


DISABLED_MESSAGE = (
    "真实设备未启用，请设置 NFS_ENABLE_REAL_HARDWARE=1 后再进行安全探测。"
)
