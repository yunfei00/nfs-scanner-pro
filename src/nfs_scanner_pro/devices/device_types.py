"""设备类型定义 — Release 018。"""

from __future__ import annotations

from enum import Enum


class DeviceType(str, Enum):
    MOTION = "motion"
    SPECTRUM = "spectrum"
    CAMERA = "camera"
    SERVO = "servo"


DEVICE_TYPE_LABELS: dict[DeviceType, str] = {
    DeviceType.MOTION: "运动平台",
    DeviceType.SPECTRUM: "频谱仪",
    DeviceType.CAMERA: "相机",
    DeviceType.SERVO: "舵机系统",
}


def device_type_label(device_type: DeviceType) -> str:
    return DEVICE_TYPE_LABELS[device_type]
