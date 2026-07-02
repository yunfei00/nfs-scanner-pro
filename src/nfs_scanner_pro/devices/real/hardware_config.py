"""真实硬件配置 — Release 036 Real Device Bridge。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def is_real_hardware_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_HARDWARE", "").strip() == "1"


def is_real_motion_jog_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_MOTION_JOG", "").strip() == "1"


def is_real_motion_move_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_MOTION_MOVE", "").strip() == "1"


def is_real_motion_home_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_MOTION_HOME", "").strip() == "1"


def is_real_motion_estop_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_MOTION_ESTOP", "").strip() == "1"


def is_real_spectrum_write_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_SPECTRUM_WRITE", "").strip() == "1"


def is_real_spectrum_sweep_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_SPECTRUM_SWEEP", "").strip() == "1"


def is_real_spectrum_trace_read_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_SPECTRUM_TRACE_READ", "").strip() == "1"


def is_real_camera_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_CAMERA", "").strip() == "1"


def is_real_servo_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_SERVO", "").strip() == "1"


def is_real_scan_execution_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_SCAN_EXECUTION", "").strip() == "1"


@dataclass
class MotionConfig:
    port: str = "COM6"
    baudrate: int = 115200
    timeout: float = 2.0


@dataclass
class MotionSafetyConfig:
    x_min: float = 0.0
    x_max: float = 200.0
    y_min: float = -200.0
    y_max: float = 0.0
    z_min: float = 0.0
    z_max: float = 50.0
    max_jog_step_mm: float = 1.0
    default_jog_step_mm: float = 0.1
    jog_feed_mm_min: float = 100.0


@dataclass
class SpectrumConfig:
    backend: str = "socket"
    host: str = "192.168.1.100"
    port: int = 5025
    timeout: float = 3.0
    visa_address: str = "TCPIP0::192.168.1.100::inst0::INSTR"

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


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
    motion_safety: MotionSafetyConfig = field(default_factory=MotionSafetyConfig)
    spectrum: SpectrumConfig = field(default_factory=SpectrumConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    servo: ServoConfig = field(default_factory=ServoConfig)


def load_motion_safety_config() -> MotionSafetyConfig:
    return MotionSafetyConfig(
        x_min=float(os.environ.get("NFS_MOTION_X_MIN", "0.0")),
        x_max=float(os.environ.get("NFS_MOTION_X_MAX", "200.0")),
        y_min=float(os.environ.get("NFS_MOTION_Y_MIN", "-200.0")),
        y_max=float(os.environ.get("NFS_MOTION_Y_MAX", "0.0")),
        z_min=float(os.environ.get("NFS_MOTION_Z_MIN", "0.0")),
        z_max=float(os.environ.get("NFS_MOTION_Z_MAX", "50.0")),
        max_jog_step_mm=float(os.environ.get("NFS_MOTION_MAX_JOG_STEP_MM", "1.0")),
        default_jog_step_mm=float(
            os.environ.get("NFS_MOTION_DEFAULT_JOG_STEP_MM", "0.1")
        ),
        jog_feed_mm_min=float(os.environ.get("NFS_MOTION_JOG_FEED_MM_MIN", "100")),
    )


def load_hardware_config() -> HardwareConfig:
    motion = MotionConfig(
        port=os.environ.get("NFS_MOTION_PORT", "COM6"),
        baudrate=int(os.environ.get("NFS_MOTION_BAUDRATE", "115200")),
        timeout=float(os.environ.get("NFS_MOTION_TIMEOUT", "2.0")),
    )
    motion_safety = load_motion_safety_config()
    host = os.environ.get("NFS_SPECTRUM_HOST", "192.168.1.100")
    port = int(os.environ.get("NFS_SPECTRUM_PORT", "5025"))
    legacy_address = os.environ.get("NFS_SPECTRUM_ADDRESS", "")
    if legacy_address and ":" in legacy_address and not os.environ.get("NFS_SPECTRUM_HOST"):
        host, _, port_text = legacy_address.rpartition(":")
        port = int(port_text)
    visa_default = f"TCPIP0::{host}::inst0::INSTR"
    spectrum = SpectrumConfig(
        backend=os.environ.get("NFS_SPECTRUM_BACKEND", "socket").strip().lower(),
        host=host,
        port=port,
        visa_address=os.environ.get("NFS_SPECTRUM_VISA_ADDRESS", visa_default),
        timeout=float(os.environ.get("NFS_SPECTRUM_TIMEOUT", "3.0")),
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
    return HardwareConfig(
        motion=motion,
        motion_safety=motion_safety,
        spectrum=spectrum,
        camera=camera,
        servo=servo,
    )


DISABLED_MESSAGE = (
    "真实设备未启用，请设置 NFS_ENABLE_REAL_HARDWARE=1 后再进行安全探测。"
)

SPECTRUM_DISABLED_MESSAGE = (
    "真实频谱仪未启用，请设置 NFS_ENABLE_REAL_HARDWARE=1"
)

JOG_DISABLED_MESSAGE = (
    "真实点动未启用，请设置 NFS_ENABLE_REAL_MOTION_JOG=1 后再进行手动点动。"
)

MOVE_DISABLED_MESSAGE = (
    "真实 move_to 未启用，请设置 NFS_ENABLE_REAL_MOTION_MOVE=1。"
)

HOME_DISABLED_MESSAGE = (
    "真实 home 未启用，请设置 NFS_ENABLE_REAL_MOTION_HOME=1。"
)

ESTOP_DISABLED_MESSAGE = (
    "真实急停未启用，请设置 NFS_ENABLE_REAL_MOTION_ESTOP=1。"
)

SPECTRUM_WRITE_DISABLED_MESSAGE = (
    "频谱仪写命令未启用，请设置 NFS_ENABLE_REAL_SPECTRUM_WRITE=1。"
)

SPECTRUM_SWEEP_DISABLED_MESSAGE = (
    "频谱 sweep 未启用，请设置 NFS_ENABLE_REAL_SPECTRUM_SWEEP=1。"
)

SPECTRUM_TRACE_DISABLED_MESSAGE = (
    "Trace 读取未启用，请设置 NFS_ENABLE_REAL_SPECTRUM_TRACE_READ=1。"
)

CAMERA_DISABLED_MESSAGE = (
    "真实相机未启用，请设置 NFS_ENABLE_REAL_CAMERA=1。"
)

SERVO_DISABLED_MESSAGE = (
    "真实舵机未启用，请设置 NFS_ENABLE_REAL_SERVO=1。"
)

SCAN_EXECUTION_DISABLED_MESSAGE = (
    "真实扫描执行未启用，请设置 NFS_ENABLE_REAL_SCAN_EXECUTION=1。"
)
