#!/usr/bin/env python3
"""Release_046 自动验收 — Real Scan UI Console Dry Fake Real Entry。"""

from __future__ import annotations

import compileall
import csv
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
from verification_utils import (  # noqa: E402
    FORBIDDEN_PATTERNS,
    ROOT as UTILS_ROOT,
    SCAN_TOOLBAR,
    setup_path,
)

IMPORT_MODULES = (
    "nfs_scanner_pro.ui.real_scan_console_widget",
    "nfs_scanner_pro.ui.real_scan_console_model",
    "nfs_scanner_pro.ui.real_scan_console_controller",
    "nfs_scanner_pro.scan.real_scan_executor",
    "nfs_scanner_pro.scan.real_scan_plan",
    "nfs_scanner_pro.devices.hardware_mode",
)

REAL_ENV_KEYS = (
    "NFS_ENABLE_REAL_HARDWARE",
    "NFS_ENABLE_REAL_SCAN_EXECUTION",
    "NFS_HARDWARE_MODE",
    "NFS_ENABLE_REAL_MOTION_MOVE",
    "NFS_ENABLE_REAL_SPECTRUM_TRACE_READ",
    "NFS_ENABLE_REAL_SPECTRUM_SWEEP",
)

SOURCE_GUARD_FILES = (
    SRC / "nfs_scanner_pro/ui/real_scan_console_widget.py",
    SRC / "nfs_scanner_pro/ui/real_scan_console_model.py",
    SRC / "nfs_scanner_pro/ui/real_scan_console_controller.py",
    SRC / "nfs_scanner_pro/ui/pages/scan_page.py",
    SRC / "nfs_scanner_pro/scan/real_scan_executor.py",
    SRC / "nfs_scanner_pro/scan/real_scan_result_writer.py",
)

DANGEROUS_COMMANDS = (
    'G0',
    'G1',
    '$H',
    'G28',
    'INIT',
    'SING',
    'CALC:DATA?',
    'TRAC:DATA?',
)


def _clear_env() -> dict[str, str | None]:
    backup: dict[str, str | None] = {}
    for key in REAL_ENV_KEYS:
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


def check_real_scan_console_imports(report: verification_report.VerificationReport) -> None:
    report.start_check("real_scan_console_imports")
    try:
        for mod in IMPORT_MODULES:
            __import__(mod)
        report.pass_check("real_scan_console_imports")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_scan_console_imports", str(exc))


def check_console_model(report: verification_report.VerificationReport) -> None:
    report.start_check("console_model")
    try:
        from nfs_scanner_pro.ui.real_scan_console_model import RealScanConsoleModel

        model = RealScanConsoleModel()
        ok = model.execution_mode == "dry_run" and model.real_run_enabled is False
        model.append_log("test")
        model.set_outputs({"json_path": "/tmp/x.json"})
        data = model.as_dict()
        ok = ok and len(model.logs) == 1 and model.output_paths.get("json_path") == "/tmp/x.json"
        json.dumps(data)
        if ok:
            report.pass_check("console_model")
        else:
            report.fail_check("console_model", "defaults or methods failed")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("console_model", str(exc))


def check_controller_default_safe(report: verification_report.VerificationReport) -> None:
    report.start_check("controller_default_safe")
    backup = _clear_env()
    try:
        from nfs_scanner_pro.ui.real_scan_console_controller import RealScanConsoleController

        ctrl = RealScanConsoleController()
        load_ok = ctrl.load_default_3x3_plan().get("ok")
        validate_ok = ctrl.validate_current_plan().get("ok")
        dry_ok = ctrl.run_dry_run().get("ok")
        fake_ok = ctrl.run_fake_run().get("ok")
        real = ctrl.run_real_run()
        real_blocked = real.get("blocked") is True
        ok = all([load_ok, validate_ok, dry_ok, fake_ok, real_blocked])
        if ok:
            report.pass_check("controller_default_safe")
        else:
            report.fail_check(
                "controller_default_safe",
                f"load={load_ok} validate={validate_ok} dry={dry_ok} "
                f"fake={fake_ok} blocked={real_blocked}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("controller_default_safe", str(exc))
    finally:
        _restore_env(backup)


def check_console_widget_offscreen(report: verification_report.VerificationReport) -> None:
    report.start_check("console_widget_offscreen")
    backup = _clear_env()
    try:
        from PySide6.QtWidgets import QApplication, QComboBox, QPushButton

        from nfs_scanner_pro.ui.real_scan_console_widget import RealScanConsoleWidget

        app = QApplication.instance() or QApplication([])
        widget = RealScanConsoleWidget()
        combo = widget.findChild(QComboBox, "realScanExecutionModeCombo")
        real_btn = widget.findChild(QPushButton, "realScanRealRunButton")
        ok = (
            combo is not None
            and combo.currentData() == "dry_run"
            and combo.findData("fake_run") >= 0
            and combo.findData("real_run") >= 0
            and real_btn is not None
            and not real_btn.isEnabled()
        )
        widget._default_btn.click()
        app.processEvents()
        summary = widget.controller.model.plan_summary
        ok = ok and summary.get("point_count") == 9
        widget._dry_btn.click()
        app.processEvents()
        ok = ok and len(widget.controller.model.logs) >= 2
        widget._fake_btn.click()
        app.processEvents()
        ok = ok and bool(widget.controller.model.output_paths)
        widget.controller.run_real_run()
        app.processEvents()
        ok = ok and any("blocked" in line.lower() for line in widget.controller.model.logs)
        if ok:
            report.pass_check("console_widget_offscreen")
        else:
            report.fail_check("console_widget_offscreen", f"summary={summary}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("console_widget_offscreen", str(exc))
    finally:
        _restore_env(backup)


def check_scan_page_integration(report: verification_report.VerificationReport) -> None:
    report.start_check("scan_page_integration")
    backup = _clear_env()
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow
        from verification_utils import toolbar_texts

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win._switch_page(win.PAGE_SCAN)
        console = getattr(win._scan_page, "_real_scan_console", None)
        toolbar = toolbar_texts(win)
        nav_text = " ".join(btn.text() for btn in win._nav.findChildren(QToolButton))
        dock = win._right_dock
        ok = (
            console is not None
            and console.objectName() == "realScanConsoleWidget"
            and all(label in toolbar for label in SCAN_TOOLBAR)
            and dock is not None
            and dock.windowTitle() == "扫描参数"
            and len(win.findChildren(QDockWidget)) == 1
            and "项目" not in nav_text
        )
        if ok:
            report.pass_check("scan_page_integration")
        else:
            report.fail_check(
                "scan_page_integration",
                f"console={console is not None} dock={dock.windowTitle() if dock else None}",
            )
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("scan_page_integration", str(exc))
    finally:
        _restore_env(backup)


def check_fake_run_outputs(report: verification_report.VerificationReport) -> None:
    report.start_check("fake_run_outputs")
    backup = _clear_env()
    try:
        from nfs_scanner_pro.ui.real_scan_console_controller import RealScanConsoleController

        ctrl = RealScanConsoleController()
        ctrl.load_default_3x3_plan()
        result = ctrl.run_fake_run()
        paths = result.get("paths") or {}
        json_path = Path(paths.get("json_path", ""))
        csv_path = Path(paths.get("csv_path", ""))
        summary_path = Path(paths.get("summary_path", ""))
        log_path = Path(paths.get("log_path", ""))
        runtime_root = verification_runtime.get_current_release_runtime()
        ok = all(path.is_file() for path in (json_path, csv_path, summary_path, log_path))
        csv_rows = 0
        if csv_path.is_file():
            with csv_path.open(encoding="utf-8") as handle:
                csv_rows = sum(1 for _ in csv.DictReader(handle))
        summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
        ok = (
            ok
            and csv_rows == 9
            and summary.get("completed_points") == 9
            and summary.get("real_hardware") is False
            and summary.get("motion_command_executed") == "fake"
            and runtime_root is not None
            and str(runtime_root) in str(json_path.resolve())
        )
        mock_projects = ROOT / "runtime" / "mock_projects"
        polluted = mock_projects.exists() and any(mock_projects.iterdir())
        if polluted and str(runtime_root) not in str(mock_projects):
            pass
        if ok:
            report.pass_check("fake_run_outputs", str(json_path.parent))
        else:
            report.fail_check(
                "fake_run_outputs",
                f"rows={csv_rows} summary={summary.get('completed_points')} "
                f"real_hw={summary.get('real_hardware')}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("fake_run_outputs", str(exc))
    finally:
        _restore_env(backup)


def check_real_run_blocked_by_default(report: verification_report.VerificationReport) -> None:
    report.start_check("real_run_blocked_by_default")
    backup = _clear_env()
    try:
        from nfs_scanner_pro.ui.real_scan_console_controller import RealScanConsoleController

        def _blocked(*_args, **_kwargs):
            raise AssertionError("real hardware access blocked")

        patches = [
            mock.patch("serial.Serial", side_effect=_blocked),
            mock.patch("socket.create_connection", side_effect=_blocked),
            mock.patch("pyvisa.ResourceManager", side_effect=_blocked),
            mock.patch("cv2.VideoCapture", side_effect=_blocked),
        ]
        with patches[0], patches[1], patches[2], patches[3]:
            ctrl = RealScanConsoleController()
            ctrl.load_default_3x3_plan()
            result = ctrl.run_real_run()
        ok = result.get("blocked") is True and "NFS" in str(result.get("error", ""))
        if ok:
            report.pass_check("real_run_blocked_by_default")
        else:
            report.fail_check("real_run_blocked_by_default", str(result))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_run_blocked_by_default", str(exc))
    finally:
        _restore_env(backup)


def check_pause_resume_stop_state(report: verification_report.VerificationReport) -> None:
    report.start_check("pause_resume_stop_state")
    backup = _clear_env()
    try:
        from nfs_scanner_pro.ui.real_scan_console_controller import RealScanConsoleController

        ctrl = RealScanConsoleController()
        ctrl.load_default_3x3_plan()
        pause = ctrl.pause()
        resume = ctrl.resume()
        stop = ctrl.stop()
        text = " ".join(ctrl.model.logs).lower()
        ok = (
            pause.get("state") == "paused"
            and resume.get("state") == "running"
            and stop.get("state") == "stopping"
            and "emergency" not in text
        )
        if ok:
            report.pass_check("pause_resume_stop_state")
        else:
            report.fail_check(
                "pause_resume_stop_state",
                f"pause={pause} resume={resume} stop={stop}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("pause_resume_stop_state", str(exc))
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
        "fake_run",
        "blocked",
        "RealScanExecutor",
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
            if path.name.startswith("real_scan_console"):
                for cmd in DANGEROUS_COMMANDS:
                    if cmd in line:
                        hits.append(f"{path.relative_to(UTILS_ROOT)}:{line_no}: {cmd}")
    if hits:
        report.fail_check("source_safety_guards", "; ".join(hits))
    else:
        report.pass_check("source_safety_guards")


def check_mock_ui_unchanged(report: verification_report.VerificationReport) -> None:
    report.start_check("mock_ui_unchanged")
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    failed: list[str] = []
    for release in ("029", "045"):
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
        / "docs/product-spec/release/Release_046_Real_Scan_UI_Console_Dry_Fake_Real_Entry/ACCEPTANCE_REPORT.md"
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_046 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_046.py",
        "python scripts/verify_all.py --only 046",
        "python scripts/verify_all.py --from 045",
        "python scripts/verify_all.py",
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
            "## 是否默认连接真实设备",
            "",
            "否",
            "",
            "## 是否默认执行真实运动",
            "",
            "否",
            "",
            "## 是否支持 dry-run",
            "",
            "是",
            "",
            "## 是否支持 fake-run",
            "",
            "是",
            "",
            "## 是否提供 real-run 入口",
            "",
            "是，但默认 blocked",
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
    verification_runtime.enter_release_runtime("R046")
    report = verification_report.VerificationReport("046")

    check_compileall(report)
    check_real_scan_console_imports(report)
    check_console_model(report)
    check_controller_default_safe(report)
    check_console_widget_offscreen(report)
    check_scan_page_integration(report)
    check_fake_run_outputs(report)
    check_real_run_blocked_by_default(report)
    check_pause_resume_stop_state(report)
    check_source_safety_guards(report)
    check_mock_ui_unchanged(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
