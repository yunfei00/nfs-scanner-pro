"""联调标准检查 — Release 048（默认不连接真实设备）。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from nfs_scanner_pro.app_paths import get_project_root
from nfs_scanner_pro.devices.hardware_mode import get_hardware_mode, is_real_mode
from nfs_scanner_pro.devices.real.hardware_config import (
    get_all_safety_flags,
    get_config_source_summary,
    is_real_hardware_enabled,
    is_real_scan_execution_enabled,
)
from nfs_scanner_pro.devices.real.real_device_manager import RealDeviceManager
from nfs_scanner_pro.hardware_commissioning.commissioning_model import (
    CommissioningGate,
    CommissioningResult,
    CommissioningSession,
)
from nfs_scanner_pro.scan.real_scan_executor import RealScanExecutor
from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan

ROOT = get_project_root()
SCRIPTS = ROOT / "scripts"

COMMISSIONING_DOCS = (
    "docs/hardware/commissioning/README.md",
    "docs/hardware/commissioning/00-overview.md",
    "docs/hardware/commissioning/10-real-run-gate.md",
)

HARDWARE_DOCS = (
    "docs/hardware/README.md",
    "docs/hardware/hardware-safety-switches.md",
    "docs/hardware/hardware-debug-command-map.md",
)


def _pass(message: str, **kwargs: Any) -> CommissioningResult:
    return CommissioningResult(ok=True, status="passed", message=message, **kwargs)


def _fail(reason: str, message: str = "", **kwargs: Any) -> CommissioningResult:
    return CommissioningResult(
        ok=False,
        status="failed",
        message=message or reason,
        fail_reason=reason,
        **kwargs,
    )


def _blocked(reason: str, **kwargs: Any) -> CommissioningResult:
    return CommissioningResult(ok=False, status="blocked", message=reason, fail_reason=reason, **kwargs)


def _skipped(reason: str, **kwargs: Any) -> CommissioningResult:
    return CommissioningResult(ok=True, status="skipped", message=reason, **kwargs)


def check_environment() -> CommissioningResult:
    missing = [name for name in ("scripts", "config", "docs/hardware") if not (ROOT / name).exists()]
    if missing:
        return _fail(f"缺少目录: {', '.join(missing)}")
    return _pass("项目目录结构完整", pass_criteria="scripts/config/docs 存在")


def check_config_files() -> CommissioningResult:
    required = (
        "config/hardware.example.yaml",
        "config/hardware.local.example.yaml",
        "config/commissioning.workflow.example.yaml",
        "config/commissioning.local.example.yaml",
    )
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        return _fail(f"缺少配置模板: {', '.join(missing)}")
    summary = get_config_source_summary()
    return _pass(
        "硬件与联调配置模板齐全",
        actual_result={"config_source": summary},
        pass_criteria="example yaml 存在",
    )


def check_safety_flags() -> CommissioningResult:
    flags = get_all_safety_flags()
    if flags.get("NFS_ENABLE_REAL_HARDWARE"):
        return _fail("验收环境不应启用 NFS_ENABLE_REAL_HARDWARE")
    return _pass("安全开关默认关闭", actual_result={"flags": flags})


def check_interface_inventory() -> CommissioningResult:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_hardware_interface_inventory.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        return _fail("接口审计失败", actual_result={"stdout": proc.stdout})
    return _pass("接口完整性审计 PASS", actual_result={"stdout": proc.stdout[:500]})


def check_cli_tools() -> CommissioningResult:
    tools = (
        "start_hardware_commissioning.py",
        "validate_commissioning_readiness.py",
        "generate_commissioning_template.py",
        "check_hardware_interface_inventory.py",
        "generate_hardware_bringup_report.py",
    )
    missing = [name for name in tools if not (SCRIPTS / name).is_file()]
    if missing:
        return _fail(f"缺少 CLI: {', '.join(missing)}")
    return _pass("联调 CLI 脚本齐全")


def check_docs() -> CommissioningResult:
    docs = list(HARDWARE_DOCS) + list(COMMISSIONING_DOCS)
    missing = [doc for doc in docs if not (ROOT / doc).is_file()]
    if missing:
        return _fail(f"缺少文档: {', '.join(missing)}")
    return _pass("硬件与联调文档齐全")


def check_motion_status_offline(*, fake: bool = False) -> CommissioningResult:
    manager = RealDeviceManager()
    if fake:
        manager.enable_fake_transports()
        manager.motion.connect()
        status = manager.motion.query_status()
        manager.disconnect_all()
        if isinstance(status, dict) and status.get("ok", True):
            return _pass("Fake 运动平台 status OK", actual_result=status)
        return _fail("Fake 运动平台 status 失败", actual_result={"status": status})
    snap = manager.motion.snapshot()
    return _pass("运动平台 snapshot 离线可读", actual_result=snap)


def check_spectrum_status_offline(*, fake: bool = False) -> CommissioningResult:
    manager = RealDeviceManager()
    if fake:
        manager.enable_fake_transports()
        manager.spectrum.connect()
        idn = manager.spectrum.query_idn()
        manager.disconnect_all()
        if isinstance(idn, dict) and idn.get("ok"):
            return _pass("Fake 频谱仪 IDN OK", actual_result=idn)
        return _fail("Fake 频谱 IDN 失败", actual_result={"idn": idn})
    snap = manager.spectrum.snapshot()
    return _pass("频谱仪 snapshot 离线可读", actual_result=snap)


def check_spectrum_marker_offline(*, fake: bool = False) -> CommissioningResult:
    if not fake:
        return _skipped("offline 模式跳过 marker 读取")
    manager = RealDeviceManager()
    manager.enable_fake_transports()
    manager.spectrum.connect()
    marker = manager.spectrum.read_marker_amplitude()
    manager.disconnect_all()
    if isinstance(marker, dict) and marker.get("ok"):
        return _pass("Fake marker 幅度 OK", actual_result=marker)
    return _fail("Fake marker 失败", actual_result={"marker": marker})


def check_camera_status_offline(*, fake: bool = False) -> CommissioningResult:
    manager = RealDeviceManager()
    if fake:
        manager.enable_fake_transports()
        manager.camera.connect()
        devices = manager.camera.enumerate_devices()
        manager.disconnect_all()
        if devices:
            return _pass("Fake 相机枚举 OK", actual_result={"devices": devices})
        return _fail("Fake 相机枚举为空")
    return _skipped("offline 模式跳过相机（可选）")


def check_servo_status_offline(*, fake: bool = False) -> CommissioningResult:
    manager = RealDeviceManager()
    if fake:
        manager.enable_fake_transports()
        manager.servo.connect()
        state = manager.servo.get_state()
        manager.disconnect_all()
        if isinstance(state, dict) and state.get("ok"):
            return _pass("Fake 舵机状态 OK", actual_result=state)
        return _fail("Fake 舵机状态失败", actual_result={"state": state})
    return _skipped("offline 模式跳过舵机（可选）")


def check_joint_sample_offline(*, fake: bool = False) -> CommissioningResult:
    if not fake:
        return _skipped("offline 模式跳过联合采样，需 fake 或 real-safe")
    manager = RealDeviceManager()
    snap = manager.joint_sample.snapshot()
    return _pass("联合采样 adapter snapshot 可读", actual_result=snap)


def check_scan_dry_run_offline() -> CommissioningResult:
    plan = generate_3x3_scan_plan()
    executor = RealScanExecutor()
    executor.load_plan(plan)
    result = executor.dry_run()
    if result.get("ok"):
        return _pass("3x3 dry-run PASS", actual_result=result, artifacts={"paths": result.get("paths", {})})
    return _fail("dry-run 失败", actual_result=result)


def check_scan_fake_run_offline() -> CommissioningResult:
    plan = generate_3x3_scan_plan()
    executor = RealScanExecutor()
    executor.load_plan(plan)
    result = executor.fake_run()
    if result.get("ok") and result.get("completed_points", 0) >= 9:
        return _pass(
            "3x3 fake-run PASS",
            actual_result=result,
            artifacts={"paths": result.get("paths", {})},
        )
    return _fail("fake-run 失败", actual_result=result)


def check_real_run_gate(session: CommissioningSession) -> CommissioningResult:
    checks = {
        "hardware_mode_real": is_real_mode(),
        "real_hardware_enabled": is_real_hardware_enabled(),
        "scan_execution_enabled": is_real_scan_execution_enabled(),
        "motion_status_passed": _step_passed(session, "motion_status"),
        "spectrum_idn_passed": _step_passed(session, "spectrum_idn"),
        "spectrum_marker_passed": _step_passed(session, "spectrum_marker"),
        "joint_sample_passed": _step_passed(session, "joint_sample"),
        "scan_plan_dry_run_passed": _step_passed(session, "scan_plan_dry_run"),
        "scan_fake_run_passed": _step_passed(session, "scan_fake_run"),
        "failure_records_empty": len(session.failure_records) == 0,
    }
    blocked = [key for key, ok in checks.items() if not ok]
    gate = CommissioningGate(
        ready=False,
        blocked_reasons=blocked,
        required_checks=checks,
        manual_confirm_complete=False,
    )
    session.gate = gate
    session.real_run_allowed = False
    message = "门禁已评估：Release_048 不执行 real-run，ready_for_real_run=false"
    if blocked:
        message += f"；未满足: {', '.join(blocked)}"
    return CommissioningResult(
        ok=True,
        status="passed",
        message=message,
        actual_result=gate.as_dict(),
        pass_criteria="门禁评估完成且 real-run 未启用",
    )


def check_real_safe_probe() -> CommissioningResult:
    if not is_real_hardware_enabled():
        return _blocked("NFS_ENABLE_REAL_HARDWARE 未设置，real-safe 探测 blocked")
    manager = RealDeviceManager()
    try:
        result = manager.test_all_safe()
        if result.get("status") == "disabled":
            return _blocked(str(result.get("message", "disabled")))
        return _pass("安全探测完成（无运动/sweep）", actual_result=result)
    finally:
        manager.disconnect_all()


def _step_passed(session: CommissioningSession, step_id: str) -> bool:
    for step in session.steps:
        if step.step_id == step_id:
            return step.status in ("passed", "skipped")
    return False
