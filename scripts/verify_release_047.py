#!/usr/bin/env python3
"""Release_047 自动验收 — Real Hardware Bring-up Readiness Pack。"""

from __future__ import annotations

import compileall
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
SRC = ROOT / "src"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import verification_report  # noqa: E402
import verification_runtime  # noqa: E402
from verification_utils import FORBIDDEN_PATTERNS, ROOT as UTILS_ROOT, setup_path  # noqa: E402

IMPORT_MODULES = ("nfs_scanner_pro.devices.real.hardware_config",)

HARDWARE_DOCS = (
    "docs/hardware/README.md",
    "docs/hardware/motion-platform-bringup.md",
    "docs/hardware/spectrum-analyzer-bringup.md",
    "docs/hardware/camera-bringup.md",
    "docs/hardware/servo-bringup.md",
    "docs/hardware/real-scan-bringup.md",
    "docs/hardware/hardware-safety-switches.md",
    "docs/hardware/hardware-debug-command-map.md",
    "docs/hardware/hardware-troubleshooting.md",
)

SAFETY_SWITCHES = (
    "NFS_HARDWARE_MODE",
    "NFS_ENABLE_REAL_HARDWARE",
    "NFS_ENABLE_REAL_MOTION_JOG",
    "NFS_ENABLE_REAL_MOTION_MOVE",
    "NFS_ENABLE_REAL_MOTION_HOME",
    "NFS_ENABLE_REAL_MOTION_ESTOP",
    "NFS_ENABLE_REAL_SPECTRUM_WRITE",
    "NFS_ENABLE_REAL_SPECTRUM_SWEEP",
    "NFS_ENABLE_REAL_SPECTRUM_TRACE_READ",
    "NFS_ENABLE_REAL_CAMERA",
    "NFS_ENABLE_REAL_SERVO",
    "NFS_ENABLE_REAL_SCAN_EXECUTION",
)

SOURCE_GUARD_FILES = (
    SRC / "nfs_scanner_pro/devices/real/hardware_config.py",
    SRC / "nfs_scanner_pro/devices/real/motion_grbl_adapter.py",
    SRC / "nfs_scanner_pro/devices/real/spectrum_scpi_adapter.py",
    SRC / "nfs_scanner_pro/devices/real/camera_adapter.py",
    SRC / "nfs_scanner_pro/devices/real/servo_adapter.py",
    SRC / "nfs_scanner_pro/devices/real/real_device_manager.py",
    SCRIPTS_DIR / "generate_hardware_bringup_report.py",
    SCRIPTS_DIR / "check_hardware_interface_inventory.py",
)

REAL_ENV_KEYS = tuple(
    key for key in SAFETY_SWITCHES if key.startswith("NFS_ENABLE_")
)


def _clear_env() -> dict[str, str | None]:
    backup: dict[str, str | None] = {}
    for key in ("NFS_HARDWARE_MODE", *REAL_ENV_KEYS, "NFS_MOTION_PORT", "NFS_SPECTRUM_HOST"):
        backup[key] = os.environ.pop(key, None)
    return backup


def _restore_env(backup: dict[str, str | None]) -> None:
    for key, value in backup.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]


def check_compileall(report: verification_report.VerificationReport) -> None:
    report.start_check("compileall")
    ok = bool(compileall.compile_dir(str(SRC / "nfs_scanner_pro"), quiet=1))
    if ok:
        for mod in IMPORT_MODULES:
            try:
                __import__(mod)
            except Exception as exc:  # noqa: BLE001
                ok = False
                report.fail_check("compileall", str(exc))
                return
        report.pass_check("compileall")
    else:
        report.fail_check("compileall")


def check_hardware_config_templates(report: verification_report.VerificationReport) -> None:
    report.start_check("hardware_config_templates")
    example = ROOT / "config/hardware.example.yaml"
    local_example = ROOT / "config/hardware.local.example.yaml"
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    ok = (
        example.is_file()
        and local_example.is_file()
        and "hardware.local.yaml" in gitignore
        and "runtime/hardware_reports/" in gitignore
    )
    if ok:
        report.pass_check("hardware_config_templates")
    else:
        report.fail_check("hardware_config_templates", "missing template or gitignore entry")


def check_hardware_config_loader(report: verification_report.VerificationReport) -> None:
    report.start_check("hardware_config_loader")
    backup = _clear_env()
    try:
        from nfs_scanner_pro.devices.real import hardware_config as hw

        hw._YAML_DATA = None
        hw._YAML_LOAD_NOTE = ""
        hw._CONFIG_SOURCES = {}
        load = hw.load_hardware_config()
        motion = hw.get_motion_config()
        spectrum = hw.get_spectrum_config()
        camera = hw.get_camera_config()
        servo = hw.get_servo_config()
        scan = hw.get_scan_config()
        summary = hw.get_config_source_summary()
        json.dumps(
            {
                "load": load.hardware_mode,
                "motion": motion,
                "spectrum": spectrum,
                "camera": camera,
                "servo": servo,
                "scan": scan,
                "summary": summary,
            }
        )
        os.environ["NFS_MOTION_PORT"] = "COM99"
        hw._YAML_DATA = None
        hw._CONFIG_SOURCES = {}
        motion2 = hw.get_motion_config()
        env_ok = motion2.get("port") == "COM99"
        if env_ok:
            report.pass_check("hardware_config_loader")
        else:
            report.fail_check("hardware_config_loader", f"port={motion2.get('port')}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("hardware_config_loader", str(exc))
    finally:
        _restore_env(backup)


def check_interface_inventory_script(report: verification_report.VerificationReport) -> None:
    report.start_check("interface_inventory_script")
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "check_hardware_interface_inventory.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = proc.stdout
    ok = (
        proc.returncode == 0
        and "MotionGrblAdapter" in out
        and "SpectrumScpiAdapter" in out
        and "CameraAdapter" in out
        and "ServoAdapter" in out
        and "RealScanExecutor" in out
        and "MISSING" not in out
    )
    if ok:
        report.pass_check("interface_inventory_script")
    else:
        report.fail_check("interface_inventory_script", proc.stdout + proc.stderr)


def check_bringup_report_generation(report: verification_report.VerificationReport) -> None:
    report.start_check("bringup_report_generation")
    backup = _clear_env()
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "generate_hardware_bringup_report.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        runtime = verification_runtime.get_current_release_runtime()
        json_path = runtime / "hardware_bringup_report.json"
        md_path = runtime / "hardware_bringup_report.md"
        data = json.loads(json_path.read_text(encoding="utf-8")) if json_path.is_file() else {}
        ok = (
            proc.returncode == 0
            and json_path.is_file()
            and md_path.is_file()
            and "hardware_mode" in data
            and "safety_flags" in data
            and "interface_inventory" in data
            and "cli_tools" in data
            and "next_manual_steps" in data
        )
        if ok:
            report.pass_check("bringup_report_generation")
        else:
            report.fail_check("bringup_report_generation", str(data.keys()))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("bringup_report_generation", str(exc))
    finally:
        _restore_env(backup)


def check_adapter_snapshots(report: verification_report.VerificationReport) -> None:
    report.start_check("adapter_snapshots")
    backup = _clear_env()
    required = ("enabled", "connected", "safe_mode", "last_error", "timestamp_iso")
    try:
        from nfs_scanner_pro.devices.real.camera_adapter import CameraAdapter
        from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter
        from nfs_scanner_pro.devices.real.real_device_manager import RealDeviceManager
        from nfs_scanner_pro.devices.real.servo_adapter import ServoAdapter
        from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter

        adapters = (
            MotionGrblAdapter(),
            SpectrumScpiAdapter(),
            CameraAdapter(),
            ServoAdapter(),
            RealDeviceManager(),
        )
        for adapter in adapters:
            snap = adapter.snapshot() if hasattr(adapter, "snapshot") else adapter.get_snapshot()
            json.dumps(snap)
            missing = [key for key in required if key not in snap]
            if missing:
                report.fail_check("adapter_snapshots", f"missing {missing} in {type(adapter).__name__}")
                return
        report.pass_check("adapter_snapshots")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("adapter_snapshots", str(exc))
    finally:
        _restore_env(backup)


def check_hardware_docs_exist(report: verification_report.VerificationReport) -> None:
    report.start_check("hardware_docs_exist")
    missing = [doc for doc in HARDWARE_DOCS if not (ROOT / doc).is_file()]
    empty = [doc for doc in HARDWARE_DOCS if (ROOT / doc).is_file() and not (ROOT / doc).read_text(encoding="utf-8").strip()]
    if missing or empty:
        report.fail_check("hardware_docs_exist", ", ".join(missing + empty))
    else:
        report.pass_check("hardware_docs_exist")


def check_safety_switch_docs(report: verification_report.VerificationReport) -> None:
    report.start_check("safety_switch_docs")
    path = ROOT / "docs/hardware/hardware-safety-switches.md"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    missing = [sw for sw in SAFETY_SWITCHES if sw not in text]
    if missing:
        report.fail_check("safety_switch_docs", ", ".join(missing))
    else:
        report.pass_check("safety_switch_docs")


def check_default_no_real_access(report: verification_report.VerificationReport) -> None:
    report.start_check("default_no_real_access")
    backup = _clear_env()

    def _blocked(*_a, **_k):
        raise AssertionError("real access blocked")

    try:
        patches = [
            mock.patch("serial.Serial", side_effect=_blocked),
            mock.patch("socket.create_connection", side_effect=_blocked),
            mock.patch("pyvisa.ResourceManager", side_effect=_blocked),
            mock.patch("cv2.VideoCapture", side_effect=_blocked),
        ]
        with patches[0], patches[1], patches[2], patches[3]:
            inv = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "check_hardware_interface_inventory.py")],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            rep = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "generate_hardware_bringup_report.py")],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        ok = inv.returncode == 0 and rep.returncode == 0
        if ok:
            report.pass_check("default_no_real_access")
        else:
            report.fail_check("default_no_real_access", inv.stderr + rep.stderr)
    except Exception as exc:  # noqa: BLE001
        report.fail_check("default_no_real_access", str(exc))
    finally:
        _restore_env(backup)


def _line_has_guard(text: str, line: str) -> bool:
    guards = (
        "is_real_hardware_enabled",
        "require_real",
        "FakeTransport",
        "_using_fake_transport",
        "NFS_ENABLE_REAL",
        "dry_run",
        "blocked",
        "safe_mode",
    )
    if any(g in line for g in guards):
        return True
    idx = text.find(line)
    if idx < 0:
        return False
    window = text[max(0, idx - 400) : idx + 200]
    return any(g in window for g in guards)


def check_source_safety_guards(report: verification_report.VerificationReport) -> None:
    report.start_check("source_safety_guards")
    hits: list[str] = []
    for path in SOURCE_GUARD_FILES:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in line and not _line_has_guard(text, line):
                    hits.append(f"{path.relative_to(UTILS_ROOT)}:{line_no}: {pattern}")
    if hits:
        report.fail_check("source_safety_guards", "; ".join(hits))
    else:
        report.pass_check("source_safety_guards")


def check_mock_ui_unchanged(report: verification_report.VerificationReport) -> None:
    report.start_check("mock_ui_unchanged")
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    failed: list[str] = []
    for release in ("029", "046"):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / f"verify_release_{release}.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        if proc.returncode != 0 or "RESULT: PASS" not in proc.stdout:
            failed.append(release)
    if failed:
        report.fail_check("mock_ui_unchanged", ", ".join(failed))
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
        / "docs/product-spec/release/Release_047_Real_Hardware_Bringup_Readiness_Pack/ACCEPTANCE_REPORT.md"
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_047 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_047.py",
        "python scripts/check_hardware_interface_inventory.py",
        "python scripts/generate_hardware_bringup_report.py",
        "```",
        "",
        "## PASS / FAIL 项",
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
            "## 是否连接真实设备",
            "",
            "否",
            "",
            "## 是否生成配置模板",
            "",
            "是",
            "",
            "## 是否生成硬件调试文档",
            "",
            "是",
            "",
            "## 是否生成诊断报告",
            "",
            "是",
            "",
            "## 是否完成接口完整性审计",
            "",
            "是" if report.is_pass() else "否",
            "",
            "## 是否修改 high_fidelity HTML",
            "",
            "否",
            "",
            "## 是否可以提交",
            "",
            "是" if report.is_pass() else "否",
            "",
            "## 结果",
            "",
            "PASS" if report.is_pass() else "FAIL",
            "",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    setup_path()
    verification_runtime.enter_release_runtime("R047")
    report = verification_report.VerificationReport("047")

    check_compileall(report)
    check_hardware_config_templates(report)
    check_hardware_config_loader(report)
    check_interface_inventory_script(report)
    check_bringup_report_generation(report)
    check_adapter_snapshots(report)
    check_hardware_docs_exist(report)
    check_safety_switch_docs(report)
    check_default_no_real_access(report)
    check_source_safety_guards(report)
    check_mock_ui_unchanged(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
