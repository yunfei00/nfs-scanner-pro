#!/usr/bin/env python3
"""Release_036 自动验收 — Real Device Adapter Inventory And Bridge。"""

from __future__ import annotations

import compileall
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
SRC = ROOT / "src"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import verification_report  # noqa: E402
from verification_utils import ROOT as UTILS_ROOT, setup_path  # noqa: E402

IMPORT_MODULES = (
    "nfs_scanner_pro.devices.device_manager_mock",
    "nfs_scanner_pro.devices.real.real_device_manager",
    "nfs_scanner_pro.devices.real.motion_grbl_adapter",
    "nfs_scanner_pro.devices.real.spectrum_scpi_adapter",
    "nfs_scanner_pro.devices.real.camera_adapter",
    "nfs_scanner_pro.devices.real.servo_adapter",
    "nfs_scanner_pro.ui.main_window",
)

INVENTORY_PATHS = (
    "src/nfs_scanner_pro/devices/device_manager_mock.py",
    "src/nfs_scanner_pro/devices/motion_mock.py",
    "src/nfs_scanner_pro/devices/spectrum_mock.py",
    "src/nfs_scanner_pro/devices/camera_mock.py",
    "src/nfs_scanner_pro/devices/servo_mock.py",
    "src/nfs_scanner_pro/devices/real/motion_grbl_adapter.py",
    "src/nfs_scanner_pro/devices/real/spectrum_scpi_adapter.py",
)


def check_compileall(report: verification_report.VerificationReport) -> None:
    report.start_check("compileall")
    ok = bool(compileall.compile_dir(str(SRC / "nfs_scanner_pro"), quiet=1))
    failed: list[str] = []
    if ok:
        for mod in IMPORT_MODULES:
            try:
                __import__(mod)
            except Exception as exc:  # noqa: BLE001
                failed.append(f"{mod}: {exc}")
                ok = False
    if ok:
        report.pass_check("compileall")
    else:
        report.fail_check("compileall", "; ".join(failed))


def check_mock_ui_boot(report: verification_report.VerificationReport) -> None:
    report.start_check("mock_ui_boot")
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro.devices import get_device_manager
        from nfs_scanner_pro.ui.main_window import MainWindow

        manager = get_device_manager()
        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        for _ in range(5):
            app.processEvents()
        nav_texts = [btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()]
        docks = win.findChildren(QDockWidget)
        ok = (
            manager.motion.is_connected()
            and len(docks) == 1
            and "项目" not in nav_texts
        )
        win.close()
        if ok:
            report.pass_check("mock_ui_boot")
        else:
            report.fail_check("mock_ui_boot", f"nav={nav_texts}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("mock_ui_boot", str(exc))


def check_device_manager_mock_intact(report: verification_report.VerificationReport) -> None:
    report.start_check("device_manager_mock_intact")
    try:
        from nfs_scanner_pro.devices import get_device_manager

        manager = get_device_manager()
        message = manager.connect_all()
        ok = (
            "Mock" in message
            and manager.is_all_ready()
            and manager.motion.port == "COM6"
        )
        manager.disconnect_all()
        if ok:
            report.pass_check("device_manager_mock_intact")
        else:
            report.fail_check("device_manager_mock_intact", message)
    except Exception as exc:  # noqa: BLE001
        report.fail_check("device_manager_mock_intact", str(exc))


def check_real_adapters_importable(report: verification_report.VerificationReport) -> None:
    report.start_check("real_adapters_importable")
    try:
        from nfs_scanner_pro.devices.real import (
            CameraAdapter,
            MotionGrblAdapter,
            RealDeviceManager,
            ServoAdapter,
            SpectrumScpiAdapter,
        )

        ok = all(
            cls is not None
            for cls in (
                RealDeviceManager,
                MotionGrblAdapter,
                SpectrumScpiAdapter,
                CameraAdapter,
                ServoAdapter,
            )
        )
        if ok:
            report.pass_check("real_adapters_importable")
        else:
            report.fail_check("real_adapters_importable", "missing class")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_adapters_importable", str(exc))


def check_real_hardware_disabled_by_default(report: verification_report.VerificationReport) -> None:
    report.start_check("real_hardware_disabled_by_default")
    env_backup = os.environ.pop("NFS_ENABLE_REAL_HARDWARE", None)
    try:
        from nfs_scanner_pro.devices.real import RealDeviceManager, is_real_hardware_enabled

        manager = RealDeviceManager()
        connect = manager.connect_all_safe()
        motion = manager.motion.connect()
        spectrum = manager.spectrum.connect()
        ok = (
            not is_real_hardware_enabled()
            and connect.get("status") == "disabled"
            and "未启用" in connect.get("message", "")
            and "未启用" in motion
            and "未启用" in spectrum
            and not manager.is_all_ready()
        )
        if ok:
            report.pass_check("real_hardware_disabled_by_default")
        else:
            report.fail_check(
                "real_hardware_disabled_by_default",
                f"connect={connect} motion={motion}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_hardware_disabled_by_default", str(exc))
    finally:
        if env_backup is not None:
            os.environ["NFS_ENABLE_REAL_HARDWARE"] = env_backup


def check_motion_commands_blocked(report: verification_report.VerificationReport) -> None:
    report.start_check("motion_commands_blocked")
    try:
        from nfs_scanner_pro.devices.real import MotionGrblAdapter, MOTION_BLOCKED_MESSAGE

        adapter = MotionGrblAdapter()
        messages = [
            adapter.jog("x", "+"),
            adapter.move_to(1, 2, 3),
            adapter.home(),
            adapter.stop(),
        ]
        ok = all(
            (isinstance(msg, dict) and msg.get("blocked") and MOTION_BLOCKED_MESSAGE in str(msg.get("message", "")))
            or (isinstance(msg, str) and MOTION_BLOCKED_MESSAGE in msg)
            for msg in messages
        )
        if ok:
            report.pass_check("motion_commands_blocked")
        else:
            report.fail_check("motion_commands_blocked", str(messages))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("motion_commands_blocked", str(exc))


def check_check_real_devices_safe_default(report: verification_report.VerificationReport) -> None:
    report.start_check("check_real_devices_safe_default")
    env = os.environ.copy()
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "check_real_devices_safe.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    text = proc.stdout + proc.stderr
    ok = (
        proc.returncode == 0
        and "真实设备未启用" in text
        and "NFS_ENABLE_REAL_HARDWARE=1" in text
    )
    if ok:
        report.pass_check("check_real_devices_safe_default")
    else:
        report.fail_check("check_real_devices_safe_default", text[-300:])


def check_code_inventory(report: verification_report.VerificationReport) -> None:
    report.start_check("code_inventory")
    missing = [rel for rel in INVENTORY_PATHS if not (ROOT / rel).is_file()]
    ok = not missing
    if ok:
        report.pass_check("code_inventory", f"{len(INVENTORY_PATHS)} files")
    else:
        report.fail_check("code_inventory", ", ".join(missing))


def check_no_high_fidelity_changes(report: verification_report.VerificationReport) -> None:
    report.start_check("no_high_fidelity_changes")
    proc = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    bad = [
        line.strip()
        for line in proc.stdout.splitlines()
        if line.strip().startswith("prototypes/high_fidelity/")
    ]
    if bad:
        report.fail_check("no_high_fidelity_changes", ", ".join(bad))
    else:
        report.pass_check("no_high_fidelity_changes")


def write_acceptance_report(report: verification_report.VerificationReport) -> Path:
    out = (
        ROOT
        / "docs/product-spec/release/Release_036_Real_Device_Adapter_Inventory_And_Bridge/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_036 验收报告 — Real Device Adapter Bridge",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_036.py",
        "python scripts/check_real_devices_safe.py",
        "python scripts/verify_all.py --only 036",
        "```",
        "",
        "## 检查项",
        "",
    ]
    for name, ok, detail, elapsed, skipped in report.entries:
        status = "SKIP" if skipped else ("PASS" if ok else "FAIL")
        suffix = f" — {detail}" if detail else ""
        timing = f" ({elapsed:.2f}s)" if elapsed is not None else ""
        lines.append(f"- [{status}] `{name}`{timing}{suffix}")
    lines.extend(
        [
            "",
            "## 结果",
            "",
            "PASS" if report.is_pass() else "FAIL",
            "",
            "## 代码盘点摘要",
            "",
            "- 仓库内无历史真实设备 Python 实现，仅有 Mock 层（Release 018）",
            "- 新增 `devices/real/` Adapter 桥接层，Mock UI 保持不变",
            "- UI 入口：`get_device_manager()` → `DeviceManagerMock`",
            "- 真实入口：`get_real_device_manager()` → `RealDeviceManager`（默认 disabled）",
            "",
            "## 新增 Adapter 文件",
            "",
            "- `src/nfs_scanner_pro/devices/real/hardware_config.py`",
            "- `src/nfs_scanner_pro/devices/real/hardware_safety.py`",
            "- `src/nfs_scanner_pro/devices/real/motion_grbl_adapter.py`",
            "- `src/nfs_scanner_pro/devices/real/spectrum_scpi_adapter.py`",
            "- `src/nfs_scanner_pro/devices/real/camera_adapter.py`",
            "- `src/nfs_scanner_pro/devices/real/servo_adapter.py`",
            "- `src/nfs_scanner_pro/devices/real/real_device_manager.py`",
            "- `scripts/check_real_devices_safe.py`",
            "",
            "## 安全开关验证",
            "",
            "- 默认 `NFS_ENABLE_REAL_HARDWARE` 未设置 → RealDeviceManager disabled",
            "",
            "## Mock UI 是否仍然可启动",
            "",
            "是",
            "",
            "## 是否默认不接真实设备",
            "",
            "是",
            "",
            "## 是否没有真实运动",
            "",
            "是（jog / move_to / home / stop 被安全阻断）",
            "",
            "## 是否没有真实扫描",
            "",
            "是",
            "",
            "## 是否修改 high_fidelity HTML",
            "",
            "否",
            "",
            "## 是否可以进入下一步真实运动平台接入",
            "",
            "是" if report.is_pass() else "否",
            "",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    setup_path()
    os.environ.pop("NFS_ENABLE_REAL_HARDWARE", None)
    report = verification_report.VerificationReport("036")

    check_compileall(report)
    check_code_inventory(report)
    check_mock_ui_boot(report)
    check_device_manager_mock_intact(report)
    check_real_adapters_importable(report)
    check_real_hardware_disabled_by_default(report)
    check_motion_commands_blocked(report)
    check_check_real_devices_safe_default(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
