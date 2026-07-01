#!/usr/bin/env python3
"""Release_038 自动验收 — Real Motion Manual Safe Jog Unlock。"""

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

MOTION_ADAPTER_PATH = SRC / "nfs_scanner_pro/devices/real/motion_grbl_adapter.py"
FORBIDDEN_SERIAL_WRITES = ("G0", "G1", "$H", "G28")


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
            is_real_motion_jog_enabled,
        )

        ok = all(
            (
                MotionGrblAdapter is not None,
                RealDeviceManager is not None,
                callable(is_real_hardware_enabled),
                callable(is_real_motion_jog_enabled),
            )
        )
        if ok:
            report.pass_check("real_motion_imports")
        else:
            report.fail_check("real_motion_imports", "missing symbol")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_motion_imports", str(exc))


def check_default_jog_disabled(report: verification_report.VerificationReport) -> None:
    report.start_check("default_jog_disabled")
    env_backup = {
        k: os.environ.pop(k, None)
        for k in ("NFS_ENABLE_REAL_HARDWARE", "NFS_ENABLE_REAL_MOTION_JOG")
    }
    try:
        from nfs_scanner_pro.devices.real import (
            MotionGrblAdapter,
            RealDeviceManager,
            is_real_hardware_enabled,
            is_real_motion_jog_enabled,
        )

        adapter = MotionGrblAdapter()
        manager = RealDeviceManager()
        jog = adapter.safe_jog("x", "+", 0.1, dry_run=False)
        ok = (
            not is_real_hardware_enabled()
            and not is_real_motion_jog_enabled()
            and adapter._serial is None
            and jog.get("blocked") is True
            and manager.connect_all_safe().get("status") == "disabled"
        )
        if ok:
            report.pass_check("default_jog_disabled")
        else:
            report.fail_check("default_jog_disabled", str(jog))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("default_jog_disabled", str(exc))
    finally:
        for key, value in env_backup.items():
            if value is not None:
                os.environ[key] = value


def check_jog_command_builder(report: verification_report.VerificationReport) -> None:
    report.start_check("jog_command_builder")
    try:
        from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter

        adapter = MotionGrblAdapter()
        cases = [
            (("x", "+", 0.1), "$J=G91 G21 X0.100 F100"),
            (("x", "-", 0.1), "$J=G91 G21 X-0.100 F100"),
            (("y", "+", 0.2), "$J=G91 G21 Y0.200 F100"),
            (("z", "-", 0.3), "$J=G91 G21 Z-0.300 F100"),
        ]
        bad: list[str] = []
        for args, expected in cases:
            got = adapter.build_jog_command(*args)
            if got != expected:
                bad.append(f"{args} -> {got!r} expected {expected!r}")
            if "G0" in got or "G1" in got:
                bad.append(f"forbidden G-code in {got!r}")
        if bad:
            report.fail_check("jog_command_builder", "; ".join(bad))
        else:
            report.pass_check("jog_command_builder")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("jog_command_builder", str(exc))


def check_soft_limit_validation(report: verification_report.VerificationReport) -> None:
    report.start_check("soft_limit_validation")
    try:
        from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter

        adapter = MotionGrblAdapter()
        pos = {"x": 10.0, "y": -10.0, "z": 5.0}
        ok_cases = [
            adapter.validate_jog("x", "+", 0.1, pos),
            adapter.validate_jog("x", "-", 0.1, pos),
        ]
        fail_z = adapter.validate_jog("z", "-", 10.0, pos)
        fail_step = adapter.validate_jog("x", "+", 99.0, pos)
        fail_axis = adapter.validate_jog("a", "+", 0.1, pos)
        fail_dir = adapter.validate_jog("x", "*", 0.1, pos)

        ok = (
            all(item.get("ok") for item in ok_cases)
            and not fail_z.get("ok")
            and not fail_step.get("ok")
            and not fail_axis.get("ok")
            and not fail_dir.get("ok")
        )
        if ok:
            report.pass_check("soft_limit_validation")
        else:
            report.fail_check(
                "soft_limit_validation",
                f"z={fail_z} step={fail_step} axis={fail_axis} dir={fail_dir}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("soft_limit_validation", str(exc))


def check_dry_run_no_motion(report: verification_report.VerificationReport) -> None:
    report.start_check("dry_run_no_motion")
    env_backup = {
        k: os.environ.get(k)
        for k in ("NFS_ENABLE_REAL_HARDWARE", "NFS_ENABLE_REAL_MOTION_JOG")
    }
    os.environ["NFS_ENABLE_REAL_HARDWARE"] = "1"
    os.environ["NFS_ENABLE_REAL_MOTION_JOG"] = "1"
    try:
        from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter

        adapter = MotionGrblAdapter()
        adapter.x = 10.0
        adapter.y = -10.0
        adapter.z = 5.0
        result = adapter.safe_jog("x", "+", 0.1, dry_run=True)
        ok = (
            result.get("ok") is True
            and result.get("dry_run") is True
            and result.get("command", "").startswith("$J=G91 G21")
            and isinstance(result.get("target_position"), dict)
            and adapter._serial is None
        )
        if ok:
            report.pass_check("dry_run_no_motion", result.get("command", ""))
        else:
            report.fail_check("dry_run_no_motion", str(result))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("dry_run_no_motion", str(exc))
    finally:
        for key in ("NFS_ENABLE_REAL_HARDWARE", "NFS_ENABLE_REAL_MOTION_JOG"):
            if env_backup.get(key) is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(env_backup[key])


def check_jog_requires_double_enable(report: verification_report.VerificationReport) -> None:
    report.start_check("jog_requires_double_enable")
    env_backup = {
        k: os.environ.get(k)
        for k in ("NFS_ENABLE_REAL_HARDWARE", "NFS_ENABLE_REAL_MOTION_JOG")
    }
    try:
        from nfs_scanner_pro.devices.real import MOTION_BLOCKED_MESSAGE, MotionGrblAdapter

        os.environ["NFS_ENABLE_REAL_HARDWARE"] = "1"
        os.environ.pop("NFS_ENABLE_REAL_MOTION_JOG", None)
        adapter = MotionGrblAdapter()
        jog = adapter.safe_jog("x", "+", 0.1, dry_run=True)
        move = adapter.move_to(1, 2, 3)
        home = adapter.home()
        ok = (
            jog.get("blocked") is True
            and jog.get("ok") is False
            and move.get("blocked") is True
            and MOTION_BLOCKED_MESSAGE in str(move.get("message", ""))
            and home.get("blocked") is True
            and MOTION_BLOCKED_MESSAGE in str(home.get("message", ""))
        )
        if ok:
            report.pass_check("jog_requires_double_enable")
        else:
            report.fail_check(
                "jog_requires_double_enable",
                f"jog={jog} move={move} home={home}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("jog_requires_double_enable", str(exc))
    finally:
        for key in ("NFS_ENABLE_REAL_HARDWARE", "NFS_ENABLE_REAL_MOTION_JOG"):
            if env_backup.get(key) is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(env_backup[key])


def check_manual_jog_script_default_safe(report: verification_report.VerificationReport) -> None:
    report.start_check("manual_jog_script_default_safe")
    env = os.environ.copy()
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    env.pop("NFS_ENABLE_REAL_MOTION_JOG", None)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    script = SCRIPTS_DIR / "manual_motion_jog_safe.py"
    proc_default = subprocess.run(
        [sys.executable, str(script), "--axis", "x", "--direction", "+", "--step", "0.1"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    proc_dry = subprocess.run(
        [
            sys.executable,
            str(script),
            "--axis",
            "x",
            "--direction",
            "+",
            "--step",
            "0.1",
            "--dry-run",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    text_default = proc_default.stdout + proc_default.stderr
    text_dry = proc_dry.stdout + proc_dry.stderr
    ok = (
        "未提供 --confirm" in text_default
        and "dry-run" in text_dry.lower()
        and "Connect" not in text_default
        and "Connect" not in text_dry
    )
    if ok:
        report.pass_check("manual_jog_script_default_safe")
    else:
        report.fail_check(
            "manual_jog_script_default_safe",
            f"default={text_default[-200:]} dry={text_dry[-200:]}",
        )


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


def check_source_motion_command_safety(report: verification_report.VerificationReport) -> None:
    report.start_check("source_motion_command_safety")
    try:
        text = MOTION_ADAPTER_PATH.read_text(encoding="utf-8")
        writes = _collect_write_literals(MOTION_ADAPTER_PATH)
        if not writes:
            report.fail_check("source_motion_command_safety", "no serial writes found")
            return
        if not all(payload == "?" for payload in writes):
            report.fail_check(
                "source_motion_command_safety",
                f"unexpected literal writes={writes!r}",
            )
            return
        if "$J=G91 G21" not in text:
            report.fail_check("source_motion_command_safety", "missing jog prefix")
            return
        if "_write_jog_command" not in text:
            report.fail_check("source_motion_command_safety", "missing jog writer")
            return
        forbidden_hits = [
            token
            for token in FORBIDDEN_SERIAL_WRITES
            if re.search(rf'write\([^\)]*{re.escape(token)}', text)
        ]
        ok = not forbidden_hits
        if ok:
            report.pass_check("source_motion_command_safety")
        else:
            report.fail_check(
                "source_motion_command_safety",
                f"forbidden={forbidden_hits}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("source_motion_command_safety", str(exc))


def check_mock_ui_unchanged(report: verification_report.VerificationReport) -> None:
    report.start_check("mock_ui_unchanged")
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    env.pop("NFS_ENABLE_REAL_MOTION_JOG", None)
    failures: list[str] = []
    for script in ("029", "037"):
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
            failures.append(f"verify_{script}={proc.returncode}")
    if failures:
        report.fail_check("mock_ui_unchanged", "; ".join(failures))
    else:
        report.pass_check("mock_ui_unchanged")


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
        / "docs/product-spec/release/Release_038_Real_Motion_Manual_Safe_Jog_Unlock/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_038 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_038.py",
        "python scripts/verify_all.py --only 038",
        "python scripts/verify_all.py --from 037",
        "python scripts/verify_all.py",
        "python scripts/manual_motion_jog_safe.py --axis x --direction + --step 0.1 --dry-run",
        "python scripts/check_real_devices_safe.py",
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
            "## 默认是否执行真实点动",
            "",
            "否",
            "",
            "## 是否需要双重开关",
            "",
            "是（NFS_ENABLE_REAL_HARDWARE=1 且 NFS_ENABLE_REAL_MOTION_JOG=1）",
            "",
            "## 是否支持 dry-run",
            "",
            "是",
            "",
            "## 是否执行 home",
            "",
            "否",
            "",
            "## 是否执行 move_to",
            "",
            "否",
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
    report = verification_report.VerificationReport("038")

    check_compileall(report)
    check_real_motion_imports(report)
    check_default_jog_disabled(report)
    check_jog_command_builder(report)
    check_soft_limit_validation(report)
    check_dry_run_no_motion(report)
    check_jog_requires_double_enable(report)
    check_manual_jog_script_default_safe(report)
    check_source_motion_command_safety(report)
    check_mock_ui_unchanged(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
