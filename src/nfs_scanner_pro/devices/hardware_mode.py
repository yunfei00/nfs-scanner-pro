"""硬件模式 — Mock / Fake / Real（Release 045）。"""

from __future__ import annotations

import os
from enum import Enum


class HardwareMode(str, Enum):
    MOCK = "mock"
    FAKE = "fake"
    REAL = "real"


_VALID = frozenset(m.value for m in HardwareMode)
_DEFAULT = HardwareMode.MOCK


def normalize_hardware_mode(value: str | HardwareMode | None) -> HardwareMode:
    if isinstance(value, HardwareMode):
        return value
    text = str(value or "").strip().lower()
    if text in _VALID:
        return HardwareMode(text)
    return _DEFAULT


def get_hardware_mode() -> HardwareMode:
    """读取当前硬件模式；环境变量 NFS_HARDWARE_MODE 优先于持久化文件。"""
    env = os.environ.get("NFS_HARDWARE_MODE", "").strip()
    if env:
        return normalize_hardware_mode(env)
    try:
        from nfs_scanner_pro.devices.hardware_mode_persistence import load_hardware_mode

        return load_hardware_mode()
    except Exception:  # noqa: BLE001
        return _DEFAULT


def set_hardware_mode(mode: str | HardwareMode) -> HardwareMode:
    """设置并持久化硬件模式（不自动连接真实设备）。"""
    normalized = normalize_hardware_mode(mode)
    from nfs_scanner_pro.devices.hardware_mode_persistence import save_hardware_mode

    save_hardware_mode(normalized)
    return normalized


def is_mock_mode() -> bool:
    return get_hardware_mode() is HardwareMode.MOCK


def is_fake_mode() -> bool:
    return get_hardware_mode() is HardwareMode.FAKE


def is_real_mode() -> bool:
    return get_hardware_mode() is HardwareMode.REAL


def hardware_mode_label(mode: HardwareMode | None = None) -> str:
    current = mode or get_hardware_mode()
    labels = {
        HardwareMode.MOCK: "Mock",
        HardwareMode.FAKE: "Fake",
        HardwareMode.REAL: "Real",
    }
    return labels.get(current, "Mock")
