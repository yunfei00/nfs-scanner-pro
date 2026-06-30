"""真实硬件安全策略 — Release 036。"""

from __future__ import annotations

from nfs_scanner_pro.devices.real.hardware_config import (
    DISABLED_MESSAGE,
    is_real_hardware_enabled,
)

MOTION_BLOCKED_MESSAGE = "真实运动命令暂未启用，请在安全确认后开启。"


def require_real_hardware_enabled() -> tuple[bool, str]:
    if is_real_hardware_enabled():
        return True, ""
    return False, DISABLED_MESSAGE


def block_motion_command(method_name: str) -> str:
    del method_name
    return MOTION_BLOCKED_MESSAGE


def block_servo_motion_command(method_name: str) -> str:
    del method_name
    return "真实舵机控制暂未启用，请在安全确认后开启。"
