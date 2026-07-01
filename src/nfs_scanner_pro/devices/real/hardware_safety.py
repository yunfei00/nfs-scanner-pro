"""真实硬件安全策略 — Release 036 / 037。"""

from __future__ import annotations

from typing import Any

from nfs_scanner_pro.devices.real.hardware_config import (
    DISABLED_MESSAGE,
    is_real_hardware_enabled,
)

MOTION_BLOCKED_MESSAGE = "真实运动命令暂未启用，本阶段只允许连接与位置读取"
MOTION_DISABLED_MESSAGE = "真实运动平台未启用，请设置 NFS_ENABLE_REAL_HARDWARE=1"


def require_real_hardware_enabled() -> tuple[bool, str]:
    if is_real_hardware_enabled():
        return True, ""
    return False, DISABLED_MESSAGE


def block_motion_command(method_name: str) -> dict[str, Any]:
    del method_name
    return {
        "ok": False,
        "blocked": True,
        "message": MOTION_BLOCKED_MESSAGE,
    }


def block_servo_motion_command(method_name: str) -> str:
    del method_name
    return "真实舵机控制暂未启用，请在安全确认后开启。"
