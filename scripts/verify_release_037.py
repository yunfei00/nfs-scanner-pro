#!/usr/bin/env python3
"""Release_037 自动验收 — Real Motion Platform Safe Connect And Position Read。"""

from __future__ import annotations

import ast
import compileall
import os
import re
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
from verification_utils import setup_path  # noqa: E402

IMPORT_MODULES = (
    "nfs_scanner_pro.devices.real.hardware_config",
    "nfs_scanner_pro.devices.real.hardware_safety",
    "nfs_scanner_pro.devices.real.real_device_manager",
    "nfs_scanner_pro.devices.real.motion_grbl_adapter",
)

TOP_MENUS = ("文件(F)", "编辑(E)", "视图(V)", "工具(T)", "设置(S)", "帮助(H)")

FORBIDDEN_MOTION_WRITES = (
    "G0",
    "G1",
    "$J",
    "$H",
    "G28",
    "M3",
    "M4",
    "M5",
    "M114",
)

MOTION_ADAPTER_PATH = SRC / "nfs_scanner_pro/devices/real/motion_grbl_adapter.py"


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


def check_real_motion_imports(report: verification_report.VerificationReport) -> None:
    report.start_check("real_motion_imports")
    try:
        from nfs_scanner_pro.devices.real import (
            MotionGrblAdapter,
            RealDeviceManager,
            is_real_hardware_enabled,
        )

        ok = MotionGrblAdapter is not None and RealDeviceManager is not None and callable(
            is_real_hardware_enabled
        )
        if ok:
            report.pass_check("real_motion_imports")
        else:
            report.fail_check("real_motion_imports", "missing symbol")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_motion_imports", str(exc))


def check_default_real_hardware_disabled(report: verification_report.VerificationReport) -> None:
    report.start_check("default_real_hardware_disabled")
    env_backup = os.environ.pop("NFS_ENABLE_REAL_HARDWARE", None)
    try:
        from nfs_scanner_pro.devices.real import (
            MOTION_DISABLED_MESSAGE,
            MotionGrblAdapter,
            RealDeviceManager,
            is_real_hardware_enabled,
        )

        adapter = MotionGrblAdapter()
        manager = RealDeviceManager()
        connect_msg = adapter.connect()
        all_safe = manager.connect_all_safe()
        ok = (
            not is_real_hardware_enabled()
            and adapter._serial is None
            and MOTION_DISABLED_MESSAGE in connect_msg
            and all_safe.get("status") == "disabled"
        )
        if ok:
            report.pass_check("default_real_hardware_disabled")
        else:
            report.fail_check(
                "default_real_hardware_disabled",
                f"connect={connect_msg!r} all={all_safe}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("default_real_hardware_disabled", str(exc))
    finally:
        if env_backup is not None:
            os.environ["NFS_ENABLE_REAL_HARDWARE"] = env_backup


def check_grbl_status_parser(report: verification_report.VerificationReport) -> None:
    report.start_check("grbl_status_parser")
    try:
        from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter

        idle = MotionGrblAdapter.parse_grbl_status_line("<Idle|MPos:0.000,1.000,2.000|FS:0,0>")
        run = MotionGrblAdapter.parse_grbl_status_line("<Run|WPos:3.100,4.200,5.300|FS:0,0>")
        bad = MotionGrblAdapter.parse_grbl_status_line("error:1")

        ok = (
            idle.get("ok")
            and idle.get("state") == "Idle"
            and idle.get("x") == 0.0
            and idle.get("y") == 1.0
            and idle.get("z") == 2.0
            and idle.get("source") == "MPos"
            and run.get("ok")
            and run.get("state") == "Run"
            and abs(run.get("x", 0) - 3.1) < 1e-6
            and abs(run.get("y", 0) - 4.2) < 1e-6
            and abs(run.get("z", 0) - 5.3) < 1e-6
            and run.get("source") == "WPos"
            and not bad.get("ok")
        )
        if ok:
            report.pass_check("grbl_status_parser")
        else:
            report.fail_check("grbl_status_parser", f"idle={idle} run={run} bad={bad}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("grbl_status_parser", str(exc))


def check_motion_commands_blocked(report: verification_report.VerificationReport) -> None:
    report.start_check("motion_commands_blocked")
    try:
        from nfs_scanner_pro.devices.real import MOTION_BLOCKED_MESSAGE, MotionGrblAdapter

        adapter = MotionGrblAdapter()
        results = [
            adapter.jog("x", "+"),
            adapter.move_to(1, 2, 3),
            adapter.home(),
            adapter.stop(),
        ]
        ok = all(
            isinstance(item, dict)
            and item.get("blocked") is True
            and item.get("ok") is False
            and MOTION_BLOCKED_MESSAGE in str(item.get("message", ""))
            for item in results
        )
        if ok:
            report.pass_check("motion_commands_blocked")
        else:
            report.fail_check("motion_commands_blocked", str(results))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("motion_commands_blocked", str(exc))


def _collect_write_literals(source_path: Path) -> list[str]:
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    literals: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and func.attr == "write"
            and isinstance(func.value, ast.Attribute)
            and func.value.attr == "_serial"
        ):
            continue
        if not node.args:
            continue
        arg = node.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, bytes):
            literals.append(arg.value.decode("latin1", errors="replace"))
    return literals


def check_safe_command_whitelist(report: verification_report.VerificationReport) -> None:
    report.start_check("safe_command_whitelist")
    try:
        writes = _collect_write_literals(MOTION_ADAPTER_PATH)
        if not writes:
            report.fail_check("safe_command_whitelist", "no serial writes found")
            return
        allowed = all(payload == "?" for payload in writes)
        forbidden_hits: list[str] = []
        text = MOTION_ADAPTER_PATH.read_text(encoding="utf-8")
        for token in FORBIDDEN_MOTION_WRITES:
            if token in text and f'write(b"{token}' in text.replace(" ", ""):
                forbidden_hits.append(token)
        ok = allowed and not forbidden_hits
        if ok:
            report.pass_check("safe_command_whitelist", f"writes={writes!r}")
        else:
            report.fail_check(
                "safe_command_whitelist",
                f"writes={writes!r} forbidden={forbidden_hits}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("safe_command_whitelist", str(exc))


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
        and "COM" not in text.split("Motion port")[0] if "Motion port" in text else True
    )
    if ok:
        report.pass_check("check_real_devices_safe_default")
    else:
        report.fail_check("check_real_devices_safe_default", text[-400:])


def check_mock_ui_unchanged(report: verification_report.VerificationReport) -> None:
    report.start_check("mock_ui_unchanged")
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    failures: list[str] = []
    for script, label in (("029", "029"), ("036", "036")):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / f"verify_release_{script}.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        text = proc.stdout + proc.stderr
        if proc.returncode != 0 or "RESULT: PASS" not in text:
            failures.append(f"verify_{label}={proc.returncode}")
    try:
        from PySide6.QtWidgets import QApplication

        from nfs_scanner_pro.devices import get_device_manager
        from nfs_scanner_pro.ui.main_window import MainWindow

        manager = get_device_manager()
        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        app.processEvents()
        if len(manager.get_device_status()) != 4:
            failures.append("device_status_count")
        win.close()
    except Exception as exc:  # noqa: BLE001
        failures.append(str(exc))
    if failures:
        report.fail_check("mock_ui_unchanged", "; ".join(failures))
    else:
        report.pass_check("mock_ui_unchanged")


def check_top_menu_always_visible(report: verification_report.VerificationReport) -> None:
    report.start_check("top_menu_always_visible")
    try:
        from PySide6.QtWidgets import QApplication

        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        app.processEvents()
        top = getattr(win, "_top_menu_bar", None)
        menu_bar = top._menu_bar if top is not None else None
        menu_texts = [a.text() for a in menu_bar.actions()] if menu_bar else []
        qss = (ROOT / "src/nfs_scanner_pro/resources/styles/dark_theme.qss").read_text(
            encoding="utf-8"
        )
        ok = (
            menu_bar is not None
            and menu_bar.isVisible()
            and all(label in menu_texts for label in TOP_MENUS)
            and ">>" not in qss
            and "fold menu" not in qss.lower()
            and "menu collapsed" not in qss.lower()
        )
        win.close()
        if ok:
            report.pass_check("top_menu_always_visible", f"menus={menu_texts}")
        else:
            report.fail_check("top_menu_always_visible", f"menus={menu_texts}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("top_menu_always_visible", str(exc))


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
        / "docs/product-spec/release/Release_037_Real_Motion_Platform_Safe_Connect_And_Position_Read/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_037 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_037.py",
        "python scripts/check_real_devices_safe.py",
        "python scripts/verify_all.py --only 037",
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
            "## 默认是否连接真实设备",
            "",
            "否",
            "",
            "## 是否执行真实运动",
            "",
            "否",
            "",
            "## 是否允许读取位置",
            "",
            "是，仅在 NFS_ENABLE_REAL_HARDWARE=1 下通过 `?` 查询 MPos/WPos",
            "",
            "## 是否修改 high_fidelity HTML",
            "",
            "否",
            "",
            "## 是否可以提交",
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
    report = verification_report.VerificationReport("037")

    check_compileall(report)
    check_real_motion_imports(report)
    check_default_real_hardware_disabled(report)
    check_grbl_status_parser(report)
    check_motion_commands_blocked(report)
    check_safe_command_whitelist(report)
    check_check_real_devices_safe_default(report)
    check_mock_ui_unchanged(report)
    check_top_menu_always_visible(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
