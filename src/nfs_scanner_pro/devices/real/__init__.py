"""真实设备 Adapter 层 — 默认关闭，需 NFS_ENABLE_REAL_HARDWARE=1。"""

from nfs_scanner_pro.devices.real.camera_adapter import CameraAdapter
from nfs_scanner_pro.devices.real.hardware_config import (
    DISABLED_MESSAGE,
    HardwareConfig,
    JOG_DISABLED_MESSAGE,
    is_real_hardware_enabled,
    is_real_motion_jog_enabled,
    load_hardware_config,
    load_motion_safety_config,
)
from nfs_scanner_pro.devices.real.hardware_safety import (
    EMERGENCY_STOP_BLOCKED_MESSAGE,
    MOTION_BLOCKED_MESSAGE,
    MOTION_DISABLED_MESSAGE,
    block_motion_command,
    block_jog_command,
    require_real_hardware_enabled,
    require_real_motion_jog_enabled,
)
from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter
from nfs_scanner_pro.devices.real.real_device_manager import RealDeviceManager, get_real_device_manager
from nfs_scanner_pro.devices.real.servo_adapter import ServoAdapter
from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter

__all__ = [
    "CameraAdapter",
    "DISABLED_MESSAGE",
    "HardwareConfig",
    "JOG_DISABLED_MESSAGE",
    "EMERGENCY_STOP_BLOCKED_MESSAGE",
    "MOTION_BLOCKED_MESSAGE",
    "MOTION_DISABLED_MESSAGE",
    "MotionGrblAdapter",
    "RealDeviceManager",
    "ServoAdapter",
    "SpectrumScpiAdapter",
    "block_jog_command",
    "block_motion_command",
    "get_real_device_manager",
    "is_real_hardware_enabled",
    "is_real_motion_jog_enabled",
    "load_motion_safety_config",
    "block_jog_command",
    "require_real_motion_jog_enabled",
    "load_hardware_config",
    "require_real_hardware_enabled",
]
