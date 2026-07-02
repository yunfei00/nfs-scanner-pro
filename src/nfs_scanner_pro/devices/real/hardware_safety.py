"""真实硬件安全策略 — Release 036 ~ 044。"""

from __future__ import annotations

from typing import Any

from nfs_scanner_pro.devices.real.hardware_config import (
    CAMERA_DISABLED_MESSAGE,
    DISABLED_MESSAGE,
    ESTOP_DISABLED_MESSAGE,
    HOME_DISABLED_MESSAGE,
    JOG_DISABLED_MESSAGE,
    MOVE_DISABLED_MESSAGE,
    SCAN_EXECUTION_DISABLED_MESSAGE,
    SERVO_DISABLED_MESSAGE,
    SPECTRUM_SWEEP_DISABLED_MESSAGE,
    SPECTRUM_TRACE_DISABLED_MESSAGE,
    SPECTRUM_WRITE_DISABLED_MESSAGE,
    is_real_camera_enabled,
    is_real_hardware_enabled,
    is_real_motion_estop_enabled,
    is_real_motion_home_enabled,
    is_real_motion_jog_enabled,
    is_real_motion_move_enabled,
    is_real_scan_execution_enabled,
    is_real_servo_enabled,
    is_real_spectrum_sweep_enabled,
    is_real_spectrum_trace_read_enabled,
    is_real_spectrum_write_enabled,
)

MOTION_BLOCKED_MESSAGE = "真实运动命令暂未启用，本阶段只允许连接与位置读取"
MOTION_DISABLED_MESSAGE = "真实运动平台未启用，请设置 NFS_ENABLE_REAL_HARDWARE=1"
EMERGENCY_STOP_BLOCKED_MESSAGE = "真实急停暂未启用，本阶段不允许发送停止命令"


def require_real_hardware_enabled() -> tuple[bool, str]:
    if is_real_hardware_enabled():
        return True, ""
    return False, DISABLED_MESSAGE


def require_real_motion_jog_enabled() -> tuple[bool, str]:
    ok_hw, msg = require_real_hardware_enabled()
    if not ok_hw:
        return False, MOTION_DISABLED_MESSAGE
    if is_real_motion_jog_enabled():
        return True, ""
    return False, JOG_DISABLED_MESSAGE


def require_real_motion_move_enabled() -> tuple[bool, str]:
    ok_hw, msg = require_real_hardware_enabled()
    if not ok_hw:
        return False, MOTION_DISABLED_MESSAGE
    if is_real_motion_move_enabled():
        return True, ""
    return False, MOVE_DISABLED_MESSAGE


def require_real_motion_home_enabled() -> tuple[bool, str]:
    ok_hw, msg = require_real_hardware_enabled()
    if not ok_hw:
        return False, MOTION_DISABLED_MESSAGE
    if is_real_motion_home_enabled():
        return True, ""
    return False, HOME_DISABLED_MESSAGE


def require_real_motion_estop_enabled() -> tuple[bool, str]:
    ok_hw, msg = require_real_hardware_enabled()
    if not ok_hw:
        return False, MOTION_DISABLED_MESSAGE
    if is_real_motion_estop_enabled():
        return True, ""
    return False, ESTOP_DISABLED_MESSAGE


def require_real_spectrum_write_enabled() -> tuple[bool, str]:
    ok_hw, msg = require_real_hardware_enabled()
    if not ok_hw:
        return False, DISABLED_MESSAGE
    if is_real_spectrum_write_enabled():
        return True, ""
    return False, SPECTRUM_WRITE_DISABLED_MESSAGE


def require_real_spectrum_sweep_enabled() -> tuple[bool, str]:
    ok_hw, msg = require_real_hardware_enabled()
    if not ok_hw:
        return False, DISABLED_MESSAGE
    if is_real_spectrum_sweep_enabled():
        return True, ""
    return False, SPECTRUM_SWEEP_DISABLED_MESSAGE


def require_real_spectrum_trace_read_enabled() -> tuple[bool, str]:
    ok_hw, msg = require_real_hardware_enabled()
    if not ok_hw:
        return False, DISABLED_MESSAGE
    if is_real_spectrum_trace_read_enabled():
        return True, ""
    return False, SPECTRUM_TRACE_DISABLED_MESSAGE


def require_real_camera_enabled() -> tuple[bool, str]:
    ok_hw, msg = require_real_hardware_enabled()
    if not ok_hw:
        return False, DISABLED_MESSAGE
    if is_real_camera_enabled():
        return True, ""
    return False, CAMERA_DISABLED_MESSAGE


def require_real_servo_enabled() -> tuple[bool, str]:
    ok_hw, msg = require_real_hardware_enabled()
    if not ok_hw:
        return False, DISABLED_MESSAGE
    if is_real_servo_enabled():
        return True, ""
    return False, SERVO_DISABLED_MESSAGE


def require_real_scan_execution_enabled() -> tuple[bool, str]:
    ok_hw, msg = require_real_hardware_enabled()
    if not ok_hw:
        return False, DISABLED_MESSAGE
    if is_real_scan_execution_enabled():
        return True, ""
    return False, SCAN_EXECUTION_DISABLED_MESSAGE


def block_motion_command(method_name: str) -> dict[str, Any]:
    del method_name
    return {
        "ok": False,
        "blocked": True,
        "message": MOTION_BLOCKED_MESSAGE,
    }


def block_jog_command(reason: str | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "blocked": True,
        "message": reason or JOG_DISABLED_MESSAGE,
    }


def block_servo_motion_command(method_name: str) -> str:
    del method_name
    return SERVO_DISABLED_MESSAGE
