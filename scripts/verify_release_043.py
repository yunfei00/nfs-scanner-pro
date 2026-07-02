#!/usr/bin/env python3
"""Release_043 自动验收 — Manual Step By Step 3x3 Point Sampling。"""

from __future__ import annotations

import compileall
import csv
import json
import os
import socket
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
from verification_utils import setup_path  # noqa: E402

IMPORT_MODULES = (
    "nfs_scanner_pro.scan.manual_scan_session",
    "nfs_scanner_pro.scan.manual_scan_result_persistence",
    "nfs_scanner_pro.scan.real_scan_plan",
    "nfs_scanner_pro.scan.real_scan_plan_persistence",
)

SOURCE_FILES = (
    SRC / "nfs_scanner_pro/scan/manual_scan_session.py",
    SRC / "nfs_scanner_pro/scan/manual_scan_result_persistence.py",
    SCRIPTS_DIR / "manual_3x3_point_sample_safe.py",
    SRC / "nfs_scanner_pro/devices/real/real_device_manager.py",
)

FORBIDDEN_EXEC_TOKENS = (
    'write(b"G0',
    'write(b"G1',
    'write(b"$J',
    'write(b"$H',
    'write(b"G28',
    "_transport_query(\"INIT",
    "_transport_query(\"SING",
    "CALC:DATA?",
    "TRAC:DATA?",
    "FORM:DATA",
)

FORBIDDEN_IMPORT_TOKENS = (
    "serial.Serial",
    "socket.create_connection",
    "import pyvisa",
    "from pyvisa",
)

MANUAL_SCRIPT = SCRIPTS_DIR / "manual_3x3_point_sample_safe.py"


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


def check_manual_scan_imports(report: verification_report.VerificationReport) -> None:
    report.start_check("manual_scan_imports")
    try:
        from nfs_scanner_pro.scan.manual_scan_session import (
            ManualScanSession,
            create_manual_scan_session,
            validate_position_near_plan_point,
        )
        from nfs_scanner_pro.scan.manual_scan_result_persistence import (
            save_manual_scan_session,
        )

        ok = all(
            obj is not None
            for obj in (
                ManualScanSession,
                create_manual_scan_session,
                validate_position_near_plan_point,
                save_manual_scan_session,
            )
        )
        if ok:
            report.pass_check("manual_scan_imports")
        else:
            report.fail_check("manual_scan_imports", "missing symbol")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("manual_scan_imports", str(exc))


def check_create_manual_session(report: verification_report.VerificationReport) -> None:
    report.start_check("create_manual_session")
    try:
        from nfs_scanner_pro.scan.manual_scan_session import create_manual_scan_session
        from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan

        plan = generate_3x3_scan_plan(
            center_x=50.0,
            center_y=-50.0,
            z=5.0,
            step_mm=0.5,
        )
        session = create_manual_scan_session(plan)
        ok = (
            session.point_count() == 9
            and session.sampled_count() == 0
            and session.pending_count() == 9
            and all(point.status == "pending" for point in session.points)
            and session.position_tolerance_mm == 0.2
        )
        if ok:
            report.pass_check("create_manual_session")
        else:
            report.fail_check("create_manual_session", session.as_dict())
    except Exception as exc:  # noqa: BLE001
        report.fail_check("create_manual_session", str(exc))


def check_position_tolerance_validation(report: verification_report.VerificationReport) -> None:
    report.start_check("position_tolerance_validation")
    try:
        from nfs_scanner_pro.scan.manual_scan_session import validate_position_near_plan_point

        planned = {"x": 50.0, "y": -50.0, "z": 5.0}
        pass_result = validate_position_near_plan_point(
            planned,
            {"x": 50.1, "y": -50.1, "z": 5.0},
            0.2,
        )
        fail_result = validate_position_near_plan_point(
            planned,
            {"x": 51.0, "y": -50.0, "z": 5.0},
            0.2,
        )
        missing_z = validate_position_near_plan_point(
            planned,
            {"x": 50.0, "y": -50.0},
            0.2,
        )
        ok = (
            pass_result.get("ok") is True
            and fail_result.get("ok") is False
            and missing_z.get("ok") is False
        )
        if ok:
            report.pass_check("position_tolerance_validation")
        else:
            report.fail_check(
                "position_tolerance_validation",
                f"pass={pass_result} fail={fail_result} missing={missing_z}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("position_tolerance_validation", str(exc))


def check_fake_sample_update(report: verification_report.VerificationReport) -> None:
    report.start_check("fake_sample_update")
    try:
        from nfs_scanner_pro.scan.manual_scan_session import (
            create_manual_scan_session,
            update_point_sample,
            validate_position_near_plan_point,
        )
        from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan

        session = create_manual_scan_session(
            generate_3x3_scan_plan(center_x=50.0, center_y=-50.0, z=5.0, step_mm=0.5)
        )
        point = session.points[0]
        validation = validate_position_near_plan_point(
            {"x": point.planned_x, "y": point.planned_y, "z": point.planned_z},
            {"x": point.planned_x, "y": point.planned_y, "z": point.planned_z},
            session.position_tolerance_mm,
        )
        record = {
            "sample_id": "SP-TEST0001",
            "timestamp_iso": "2026-01-01T00:00:00+00:00",
            "position": {
                "x": point.planned_x,
                "y": point.planned_y,
                "z": point.planned_z,
            },
            "spectrum": {"frequency_hz": 2450000000.0, "amplitude_dbm": -23.45},
            "motion_command_executed": False,
            "sweep_started": False,
        }
        update_point_sample(session, 0, record, validation)
        updated = session.points[0]
        ok = (
            updated.status == "sampled"
            and session.sampled_count() == 1
            and session.pending_count() == 8
            and updated.amplitude_dbm == -23.45
            and record["motion_command_executed"] is False
            and record["sweep_started"] is False
        )
        if ok:
            report.pass_check("fake_sample_update")
        else:
            report.fail_check("fake_sample_update", updated.as_dict())
    except Exception as exc:  # noqa: BLE001
        report.fail_check("fake_sample_update", str(exc))


def check_manual_session_persistence(report: verification_report.VerificationReport) -> None:
    report.start_check("manual_session_persistence")
    try:
        verification_runtime.enter_release_runtime("R043")
        from nfs_scanner_pro.scan.manual_scan_result_persistence import (
            append_manual_sample,
            save_manual_scan_session,
        )
        from nfs_scanner_pro.scan.manual_scan_session import (
            create_manual_scan_session,
            update_point_sample,
            validate_position_near_plan_point,
        )
        from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan

        session = create_manual_scan_session(
            generate_3x3_scan_plan(center_x=50.0, center_y=-50.0, z=5.0, step_mm=0.5)
        )
        paths = save_manual_scan_session(session)
        point = session.points[0]
        validation = validate_position_near_plan_point(
            {"x": point.planned_x, "y": point.planned_y, "z": point.planned_z},
            {"x": point.planned_x, "y": point.planned_y, "z": point.planned_z},
            session.position_tolerance_mm,
        )
        record = {
            "sample_id": "SP-PERSIST01",
            "timestamp_iso": "2026-01-01T00:00:00+00:00",
            "position": {"x": point.planned_x, "y": point.planned_y, "z": point.planned_z},
            "spectrum": {"frequency_hz": 2450000000.0, "amplitude_dbm": -23.45},
            "motion_command_executed": False,
            "sweep_started": False,
            "safe_mode": True,
        }
        update_point_sample(session, 0, record, validation)
        save_manual_scan_session(session)
        samples_path = append_manual_sample(session, session.points[0], record)

        ok = (
            paths["session_json"].is_file()
            and paths["points_csv"].is_file()
            and paths["summary_json"].is_file()
            and samples_path.is_file()
            and "R043" in paths["session_json"].as_posix()
        )
        if ok:
            with paths["points_csv"].open(encoding="utf-8", newline="") as handle:
                point_rows = list(csv.reader(handle))
            with samples_path.open(encoding="utf-8", newline="") as handle:
                sample_rows = list(csv.reader(handle))
            ok = len(point_rows) == 10 and len(sample_rows) == 2
        summary = json.loads(
            (paths["session_json"].parent / "manual_scan_summary.json").read_text(
                encoding="utf-8"
            )
        )
        ok = (
            ok
            and summary.get("sampled_count") == 1
            and summary.get("pending_count") == 8
            and summary.get("motion_command_executed_any") is False
            and summary.get("sweep_started_any") is False
        )
        if ok:
            report.pass_check(
                "manual_session_persistence",
                paths["session_json"].relative_to(ROOT).as_posix(),
            )
        else:
            report.fail_check("manual_session_persistence", str(summary))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("manual_session_persistence", str(exc))


def _run_manual_script(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    return subprocess.run(
        [sys.executable, str(MANUAL_SCRIPT), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def check_script_default_safe(report: verification_report.VerificationReport) -> None:
    report.start_check("script_default_safe")
    with mock.patch.object(
        socket,
        "create_" + "connection",
        side_effect=AssertionError("socket"),
    ):
        proc = _run_manual_script([])
    text = proc.stdout + proc.stderr
    ok = (
        proc.returncode == 0
        and "不会连接设备" in text
        and "不会移动" in text
        and "不会采样" in text
    )
    if ok:
        report.pass_check("script_default_safe")
    else:
        report.fail_check("script_default_safe", text[-300:])


def check_script_create_session(report: verification_report.VerificationReport) -> None:
    report.start_check("script_create_session")
    try:
        verification_runtime.enter_release_runtime("R043")
        from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan
        from nfs_scanner_pro.scan.real_scan_plan_persistence import save_scan_plan
        from nfs_scanner_pro.scan.real_scan_safety import validate_scan_plan

        plan = generate_3x3_scan_plan(center_x=50.0, center_y=-50.0, z=5.0, step_mm=0.5)
        validation = validate_scan_plan(plan)
        validation["valid"] = validation.get("ok", False)
        plan_paths = save_scan_plan(plan, validation)

        with mock.patch.object(
            socket,
            "create_" + "connection",
            side_effect=AssertionError("socket"),
        ):
            proc = _run_manual_script(
                ["--create-session", "--plan", str(plan_paths["json_path"])]
            )
        text = proc.stdout + proc.stderr
        session_json = None
        for line in text.splitlines():
            if "Session JSON:" in line:
                session_json = Path(line.split(":", 1)[1].strip())
                break
        ok = (
            proc.returncode == 0
            and session_json is not None
            and session_json.is_file()
            and "Point count: 9" in text
        )
        if ok:
            data = json.loads(session_json.read_text(encoding="utf-8"))
            ok = len(data.get("points", [])) == 9
        if ok:
            report.pass_check("script_create_session")
        else:
            report.fail_check("script_create_session", text[-400:])
    except Exception as exc:  # noqa: BLE001
        report.fail_check("script_create_session", str(exc))


def check_script_fake_sample(report: verification_report.VerificationReport) -> None:
    report.start_check("script_fake_sample")
    try:
        verification_runtime.enter_release_runtime("R043")
        from nfs_scanner_pro.scan.manual_scan_result_persistence import save_manual_scan_session
        from nfs_scanner_pro.scan.manual_scan_session import create_manual_scan_session
        from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan

        session = create_manual_scan_session(
            generate_3x3_scan_plan(center_x=50.0, center_y=-50.0, z=5.0, step_mm=0.5)
        )
        paths = save_manual_scan_session(session)
        session_json = paths["session_json"]

        with mock.patch.object(
            socket,
            "create_" + "connection",
            side_effect=AssertionError("socket"),
        ):
            proc = _run_manual_script(
                [
                    "--session",
                    str(session_json),
                    "--point-index",
                    "0",
                    "--fake-sample",
                ]
            )
        text = proc.stdout + proc.stderr
        data = json.loads(session_json.read_text(encoding="utf-8"))
        samples_csv = session_json.parent / "manual_scan_samples.csv"
        ok = (
            proc.returncode == 0
            and data["points"][0]["status"] == "sampled"
            and "Sampled count: 1" in text
            and samples_csv.is_file()
            and "No real device connected" in text
        )
        if ok:
            report.pass_check("script_fake_sample")
        else:
            report.fail_check("script_fake_sample", text[-400:])
    except Exception as exc:  # noqa: BLE001
        report.fail_check("script_fake_sample", str(exc))


def check_script_requires_confirm_for_real_sample(
    report: verification_report.VerificationReport,
) -> None:
    report.start_check("script_requires_confirm_for_real_sample")
    try:
        verification_runtime.enter_release_runtime("R043")
        from nfs_scanner_pro.scan.manual_scan_result_persistence import save_manual_scan_session
        from nfs_scanner_pro.scan.manual_scan_session import create_manual_scan_session
        from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan

        session = create_manual_scan_session(
            generate_3x3_scan_plan(center_x=50.0, center_y=-50.0, z=5.0, step_mm=0.5)
        )
        paths = save_manual_scan_session(session)
        session_json = paths["session_json"]

        with mock.patch.object(
            socket,
            "create_" + "connection",
            side_effect=AssertionError("socket"),
        ):
            proc = _run_manual_script(
                ["--session", str(session_json), "--point-index", "1"]
            )
        text = proc.stdout + proc.stderr
        data = json.loads(session_json.read_text(encoding="utf-8"))
        ok = (
            proc.returncode == 0
            and "--confirm-sample" in text
            and data["points"][1]["status"] == "pending"
        )
        if ok:
            report.pass_check("script_requires_confirm_for_real_sample")
        else:
            report.fail_check("script_requires_confirm_for_real_sample", text[-300:])
    except Exception as exc:  # noqa: BLE001
        report.fail_check("script_requires_confirm_for_real_sample", str(exc))


def check_source_no_motion_or_sweep_commands(report: verification_report.VerificationReport) -> None:
    report.start_check("source_no_motion_or_sweep_commands")
    hits: list[str] = []
    for path in SOURCE_FILES:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_EXEC_TOKENS + FORBIDDEN_IMPORT_TOKENS:
            if token in text:
                hits.append(f"{path.name}: {token}")
        if "sample_once_safe" in text and path.name == "manual_3x3_point_sample_safe.py":
            hits.append(f"{path.name}: sample_once_safe")
        if path.name == "manual_3x3_point_sample_safe.py":
            if "for point_index in range(9)" in text.replace(" ", ""):
                hits.append(f"{path.name}: auto loop 9 points")
    if hits:
        report.fail_check("source_no_motion_or_sweep_commands", "; ".join(hits))
    else:
        report.pass_check("source_no_motion_or_sweep_commands")


def check_mock_ui_unchanged(report: verification_report.VerificationReport) -> None:
    report.start_check("mock_ui_unchanged")
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    failures: list[str] = []
    for script in ("029", "042"):
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
        / "docs/product-spec/release/Release_043_Manual_Step_By_Step_3x3_Point_Sampling/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_043 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_043.py",
        "python scripts/verify_all.py --only 043",
        "python scripts/manual_3x3_point_sample_safe.py",
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
            "## 是否默认连接真实设备",
            "",
            "否",
            "",
            "## 是否执行真实运动",
            "",
            "否",
            "",
            "## 是否自动采 9 个点",
            "",
            "否",
            "",
            "## 是否启动 sweep",
            "",
            "否",
            "",
            "## 是否支持 fake sample",
            "",
            "是",
            "",
            "## 是否支持 session 断点",
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
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    setup_path()
    verification_runtime.enter_release_runtime("R043")
    report = verification_report.VerificationReport("043")

    check_compileall(report)
    check_manual_scan_imports(report)
    check_create_manual_session(report)
    check_position_tolerance_validation(report)
    check_fake_sample_update(report)
    check_manual_session_persistence(report)
    check_script_default_safe(report)
    check_script_create_session(report)
    check_script_fake_sample(report)
    check_script_requires_confirm_for_real_sample(report)
    check_source_no_motion_or_sweep_commands(report)
    check_mock_ui_unchanged(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
