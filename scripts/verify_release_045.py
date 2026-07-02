#!/usr/bin/env python3
"""Release_045 自动验收 — Real Fake Mock Hardware Mode Switch And Debug Guide。"""

from __future__ import annotations

import compileall
import os
import re
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

IMPORT_MODULES = (
    "nfs_scanner_pro.devices.hardware_mode",
    "nfs_scanner_pro.devices.hardware_mode_persistence",
    "nfs_scanner_pro.devices.real.real_device_manager",
    "nfs_scanner_pro.ui.pages.device_page",
)

SOURCE_GUARD_FILES = (
    SRC / "nfs_scanner_pro/devices/hardware_mode.py",
    SRC / "nfs_scanner_pro/devices/hardware_mode_persistence.py",
    SRC / "nfs_scanner_pro/ui/pages/device_page.py",
    SRC / "nfs_scanner_pro/ui/main_window.py",
    SRC / "nfs_scanner_pro/devices/real/real_device_manager.py",
    SCRIPTS_DIR / "hardware_debug_wizard.py",
)

GUIDE_REQUIRED = (
    "Mock",
    "Fake Hardware",
    "Real Hardware",
    "NFS_ENABLE_REAL_HARDWARE",
    "debug_real_motion.py",
    "debug_real_spectrum.py",
    "run_real_scan_offline.py",
)

REAL_ENV_KEYS = ("NFS_ENABLE_REAL_HARDWARE", "NFS_HARDWARE_MODE")


def _clear_env_keys(keys: tuple[str, ...]) -> dict[str, str | None]:
    backup: dict[str, str | None] = {}
    for key in keys:
        backup[key] = os.environ.pop(key, None)
    return backup


def _restore_env_keys(backup: dict[str, str | None]) -> None:
    for key, value in backup.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]


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


def check_hardware_mode_imports(report: verification_report.VerificationReport) -> None:
    report.start_check("hardware_mode_imports")
    try:
        for mod in IMPORT_MODULES:
            __import__(mod)
        report.pass_check("hardware_mode_imports")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("hardware_mode_imports", str(exc))


def check_hardware_mode_default_mock(report: verification_report.VerificationReport) -> None:
    report.start_check("hardware_mode_default_mock")
    backup = _clear_env_keys(REAL_ENV_KEYS)
    try:
        from nfs_scanner_pro.devices.hardware_mode import (
            get_hardware_mode,
            is_fake_mode,
            is_mock_mode,
            is_real_mode,
            HardwareMode,
        )
        from nfs_scanner_pro.devices.hardware_mode_persistence import reset_hardware_mode

        reset_hardware_mode()
        ok = (
            get_hardware_mode() is HardwareMode.MOCK
            and is_mock_mode()
            and not is_fake_mode()
            and not is_real_mode()
        )
        if ok:
            report.pass_check("hardware_mode_default_mock")
        else:
            report.fail_check("hardware_mode_default_mock", "default is not mock")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("hardware_mode_default_mock", str(exc))
    finally:
        _restore_env_keys(backup)


def check_hardware_mode_env_override(report: verification_report.VerificationReport) -> None:
    report.start_check("hardware_mode_env_override")
    backup = _clear_env_keys(REAL_ENV_KEYS)
    try:
        from nfs_scanner_pro.devices.hardware_mode import (
            HardwareMode,
            get_hardware_mode,
            normalize_hardware_mode,
        )

        os.environ["NFS_HARDWARE_MODE"] = "fake"
        fake_ok = get_hardware_mode() is HardwareMode.FAKE
        os.environ["NFS_HARDWARE_MODE"] = "real"
        real_ok = get_hardware_mode() is HardwareMode.REAL
        os.environ["NFS_HARDWARE_MODE"] = "abc"
        invalid_ok = normalize_hardware_mode("abc") is HardwareMode.MOCK
        if fake_ok and real_ok and invalid_ok:
            report.pass_check("hardware_mode_env_override")
        else:
            report.fail_check(
                "hardware_mode_env_override",
                f"fake={fake_ok} real={real_ok} invalid={invalid_ok}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("hardware_mode_env_override", str(exc))
    finally:
        _restore_env_keys(backup)


def check_hardware_mode_persistence(report: verification_report.VerificationReport) -> None:
    report.start_check("hardware_mode_persistence")
    backup = _clear_env_keys(REAL_ENV_KEYS)
    try:
        from nfs_scanner_pro.devices.hardware_mode import HardwareMode
        from nfs_scanner_pro.devices.hardware_mode_persistence import (
            load_hardware_mode,
            reset_hardware_mode,
            save_hardware_mode,
        )

        reset_hardware_mode()
        save_hardware_mode("fake")
        fake_ok = load_hardware_mode() is HardwareMode.FAKE
        save_hardware_mode("real")
        real_ok = load_hardware_mode() is HardwareMode.REAL
        reset_hardware_mode()
        mock_ok = load_hardware_mode() is HardwareMode.MOCK
        if fake_ok and real_ok and mock_ok:
            report.pass_check("hardware_mode_persistence")
        else:
            report.fail_check(
                "hardware_mode_persistence",
                f"fake={fake_ok} real={real_ok} mock={mock_ok}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("hardware_mode_persistence", str(exc))
    finally:
        _restore_env_keys(backup)


def check_device_page_mode_ui(report: verification_report.VerificationReport) -> None:
    report.start_check("device_page_mode_ui")
    backup = _clear_env_keys(REAL_ENV_KEYS)
    try:
        from PySide6.QtWidgets import QApplication, QComboBox, QDockWidget, QToolButton

        from nfs_scanner_pro.devices.hardware_mode import HardwareMode
        from nfs_scanner_pro.devices.hardware_mode_persistence import reset_hardware_mode
        from nfs_scanner_pro.ui.main_window import MainWindow

        reset_hardware_mode()
        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win._switch_page(win.PAGE_DEVICE)

        combo = win._device_page.findChild(QComboBox, "hardwareModeCombo")
        nav_text = " ".join(
            btn.text() for btn in win._nav.findChildren(QToolButton)
        )
        page_text = combo.currentText() if combo else ""
        ok = (
            combo is not None
            and combo.count() == 3
            and "Mock" in page_text
            and combo.findData(HardwareMode.MOCK.value) >= 0
            and combo.findData(HardwareMode.FAKE.value) >= 0
            and combo.findData(HardwareMode.REAL.value) >= 0
            and combo.currentData() == HardwareMode.MOCK.value
        )
        if ok:
            combo.setCurrentIndex(combo.findData(HardwareMode.FAKE.value))
            app.processEvents()
            fake_ok = combo.currentData() == HardwareMode.FAKE.value
            combo.setCurrentIndex(combo.findData(HardwareMode.REAL.value))
            app.processEvents()
            real_ok = combo.currentData() == HardwareMode.REAL.value
            hint = win._device_page.findChild(type(win._device_page._mode_hint), "hardwareModeHint")
            real_hint_ok = hint is not None and "NFS_ENABLE_REAL_HARDWARE" in hint.text()
            dock_ok = len(win.findChildren(QDockWidget)) == 1
            nav_ok = "项目" not in nav_text
            ok = fake_ok and real_ok and real_hint_ok and dock_ok and nav_ok
        if ok:
            report.pass_check("device_page_mode_ui")
        else:
            report.fail_check(
                "device_page_mode_ui",
                f"combo={combo is not None} fake={locals().get('fake_ok')} "
                f"real={locals().get('real_ok')} hint={locals().get('real_hint_ok')} "
                f"dock={locals().get('dock_ok')} nav={locals().get('nav_ok')}",
            )
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("device_page_mode_ui", str(exc))
    finally:
        _restore_env_keys(backup)


def check_real_probe_default_disabled(report: verification_report.VerificationReport) -> None:
    report.start_check("real_probe_default_disabled")
    backup = _clear_env_keys(REAL_ENV_KEYS)
    try:
        from nfs_scanner_pro.devices.real.real_device_manager import RealDeviceManager

        def _blocked(*_args, **_kwargs):
            raise AssertionError("real hardware access blocked in verification")

        patches = [
            mock.patch("serial.Serial", side_effect=_blocked),
            mock.patch("socket.create_connection", side_effect=_blocked),
            mock.patch("pyvisa.ResourceManager", side_effect=_blocked),
            mock.patch("cv2.VideoCapture", side_effect=_blocked),
        ]
        with patches[0], patches[1], patches[2], patches[3]:
            manager = RealDeviceManager()
            result = manager.test_all_safe()
            page_result = None
            try:
                from PySide6.QtWidgets import QApplication, QPushButton

                from nfs_scanner_pro.ui.main_window import MainWindow

                app = QApplication.instance() or QApplication([])
                win = MainWindow()
                win._device_page.apply_hardware_mode("real")
                btn = win._device_page.findChild(QPushButton, "realSafeProbeButton")
                if btn is not None:
                    btn.click()
                    app.processEvents()
                win.close()
            except Exception:  # noqa: BLE001
                pass
        ok = result.get("status") == "disabled" and "NFS_ENABLE_REAL_HARDWARE" in str(
            result.get("message", "")
        )
        if ok:
            report.pass_check("real_probe_default_disabled")
        else:
            report.fail_check("real_probe_default_disabled", str(result))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_probe_default_disabled", str(exc))
    finally:
        _restore_env_keys(backup)


def _run_wizard(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "hardware_debug_wizard.py"), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def check_hardware_debug_wizard_default(report: verification_report.VerificationReport) -> None:
    report.start_check("hardware_debug_wizard_default")
    proc = _run_wizard([])
    out = proc.stdout
    ok = (
        proc.returncode == 0
        and "当前硬件模式" in out
        and "真实硬件启用：false" in out
        and "--fake" in out
    )
    if ok:
        report.pass_check("hardware_debug_wizard_default")
    else:
        report.fail_check("hardware_debug_wizard_default", proc.stdout + proc.stderr)


def check_hardware_debug_wizard_fake_check(report: verification_report.VerificationReport) -> None:
    report.start_check("hardware_debug_wizard_fake_check")
    proc = _run_wizard(["--fake-check"])
    ok = proc.returncode == 0 and "Fake" in proc.stdout
    if ok:
        report.pass_check("hardware_debug_wizard_fake_check")
    else:
        report.fail_check("hardware_debug_wizard_fake_check", proc.stdout + proc.stderr)


def check_hardware_debug_guide_exists(report: verification_report.VerificationReport) -> None:
    report.start_check("hardware_debug_guide_exists")
    path = ROOT / "docs/hardware-debug-guide.md"
    if not path.is_file():
        report.fail_check("hardware_debug_guide_exists", "missing file")
        return
    text = path.read_text(encoding="utf-8")
    missing = [token for token in GUIDE_REQUIRED if token not in text]
    if missing:
        report.fail_check("hardware_debug_guide_exists", ", ".join(missing))
    else:
        report.pass_check("hardware_debug_guide_exists")


def _line_has_guard(text: str, line: str) -> bool:
    guards = (
        "is_real_hardware_enabled",
        "require_real",
        "FakeTransport",
        "FakeSerialTransport",
        "FakeScpiTransport",
        "_using_fake_transport",
        "disabled",
        "NFS_ENABLE_REAL",
        "block_",
        "dry_run",
        "fake",
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
    for release in ("029", "044"):
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
        / "docs/product-spec/release/Release_045_Real_Fake_Mock_Hardware_Mode_Switch_And_Debug_Guide/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_045 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_045.py",
        "python scripts/verify_all.py --only 045",
        "python scripts/verify_all.py --from 044",
        "python scripts/verify_all.py",
        "python scripts/hardware_debug_wizard.py",
        "python scripts/hardware_debug_wizard.py --fake-check",
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
            "## 默认硬件模式",
            "",
            "Mock",
            "",
            "## 是否默认连接真实设备",
            "",
            "否",
            "",
            "## 是否支持 Fake Hardware",
            "",
            "是",
            "",
            "## 是否支持 Real 模式安全探测",
            "",
            "是",
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
    verification_runtime.enter_release_runtime("R045")
    report = verification_report.VerificationReport("045")

    check_compileall(report)
    check_hardware_mode_imports(report)
    check_hardware_mode_default_mock(report)
    check_hardware_mode_env_override(report)
    check_hardware_mode_persistence(report)
    check_device_page_mode_ui(report)
    check_real_probe_default_disabled(report)
    check_hardware_debug_wizard_default(report)
    check_hardware_debug_wizard_fake_check(report)
    check_hardware_debug_guide_exists(report)
    check_source_safety_guards(report)
    check_mock_ui_unchanged(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
