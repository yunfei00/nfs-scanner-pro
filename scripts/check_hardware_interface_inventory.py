#!/usr/bin/env python3
"""真实硬件接口完整性审计 — Release 047。"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.devices.real.camera_adapter import CameraAdapter  # noqa: E402
from nfs_scanner_pro.devices.real.hardware_config import get_all_safety_flags  # noqa: E402
from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter  # noqa: E402
from nfs_scanner_pro.devices.real.real_device_manager import RealDeviceManager  # noqa: E402
from nfs_scanner_pro.devices.real.servo_adapter import ServoAdapter  # noqa: E402
from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter  # noqa: E402
from nfs_scanner_pro.scan.real_scan_executor import RealScanExecutor  # noqa: E402

REQUIRED: dict[str, tuple[str, ...]] = {
    "MotionGrblAdapter": (
        "connect",
        "disconnect",
        "is_connected",
        "query_status",
        "refresh_position",
        "safe_jog",
        "move_to",
        "home",
        "emergency_stop",
        "snapshot",
    ),
    "SpectrumScpiAdapter": (
        "connect",
        "disconnect",
        "is_connected",
        "query",
        "write",
        "query_idn",
        "query_system_error",
        "get_current_frequency",
        "read_marker_amplitude",
        "read_trace_info",
        "read_trace_data",
        "configure_measurement",
        "trigger_single_sweep",
        "read_single_point_amplitude",
        "snapshot",
    ),
    "CameraAdapter": (
        "enumerate_devices",
        "connect",
        "disconnect",
        "is_connected",
        "capture_image",
        "snapshot",
    ),
    "ServoAdapter": (
        "connect",
        "disconnect",
        "is_connected",
        "get_state",
        "switch_hx",
        "switch_hy",
        "calibrate",
        "snapshot",
    ),
    "RealDeviceManager": (
        "connect_all_safe",
        "disconnect_all",
        "test_all_safe",
        "get_snapshot",
        "get_device_status",
    ),
    "RealScanExecutor": (
        "load_plan",
        "dry_run",
        "fake_run",
        "real_run",
        "pause",
        "resume",
        "stop",
        "snapshot",
    ),
}

CLASS_MAP = {
    "MotionGrblAdapter": MotionGrblAdapter,
    "SpectrumScpiAdapter": SpectrumScpiAdapter,
    "CameraAdapter": CameraAdapter,
    "ServoAdapter": ServoAdapter,
    "RealDeviceManager": RealDeviceManager,
    "RealScanExecutor": RealScanExecutor,
}

CLI_SCRIPTS = (
    "debug_real_motion.py",
    "debug_real_spectrum.py",
    "debug_real_camera.py",
    "debug_real_servo.py",
    "hardware_debug_wizard.py",
    "run_real_scan_offline.py",
    "generate_hardware_bringup_report.py",
    "check_hardware_interface_inventory.py",
)


def _audit_class(name: str, cls: type) -> tuple[list[str], list[str]]:
    present = sorted(
        member
        for member, obj in inspect.getmembers(cls)
        if member in REQUIRED[name] and (inspect.isfunction(obj) or inspect.ismethoddescriptor(obj))
    )
    missing = [method for method in REQUIRED[name] if method not in present]
    return present, missing


def main() -> int:
    print("Hardware Interface Inventory")
    print("")
    all_missing: dict[str, list[str]] = {}
    inventory: dict[str, list[str]] = {}
    for name, cls in CLASS_MAP.items():
        present, missing = _audit_class(name, cls)
        inventory[name] = present
        all_missing[name] = missing
        print(f"{name}:")
        for method in REQUIRED[name]:
            mark = "OK" if method in present else "MISSING"
            print(f"  [{mark}] {method}")
        print("")

    print("缺失接口列表:")
    flat_missing = [f"{cls}.{method}" for cls, methods in all_missing.items() for method in methods]
    if flat_missing:
        for item in flat_missing:
            print(f"  - {item}")
    else:
        print("  (无)")
    print("")

    print("安全开关列表:")
    for key, value in sorted(get_all_safety_flags().items()):
        print(f"  {key}={str(value).lower()}")
    print("")

    print("CLI 脚本列表:")
    scripts_dir = ROOT / "scripts"
    for script in CLI_SCRIPTS:
        path = scripts_dir / script
        status = "OK" if path.is_file() else "MISSING"
        print(f"  [{status}] {script}")
    print("")

    missing_scripts = [s for s in CLI_SCRIPTS if not (scripts_dir / s).is_file()]
    failed = bool(flat_missing or missing_scripts)
    print("RESULT:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
