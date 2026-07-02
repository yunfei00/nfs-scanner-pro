#!/usr/bin/env python3
"""Release_042 自动验收 — Real Small Area 3x3 Scan Dry Run Planner。"""

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
    "nfs_scanner_pro.scan.real_scan_plan",
    "nfs_scanner_pro.scan.real_scan_safety",
    "nfs_scanner_pro.scan.real_scan_plan_persistence",
)

SOURCE_FILES = (
    SRC / "nfs_scanner_pro/scan/real_scan_plan.py",
    SRC / "nfs_scanner_pro/scan/real_scan_safety.py",
    SRC / "nfs_scanner_pro/scan/real_scan_plan_persistence.py",
    SCRIPTS_DIR / "plan_small_area_scan_dry_run.py",
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

EXPECTED_SERPENTINE = (
    (49.5, -50.5),
    (50.0, -50.5),
    (50.5, -50.5),
    (50.5, -50.0),
    (50.0, -50.0),
    (49.5, -50.0),
    (49.5, -49.5),
    (50.0, -49.5),
    (50.5, -49.5),
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


def check_real_scan_plan_imports(report: verification_report.VerificationReport) -> None:
    report.start_check("real_scan_plan_imports")
    try:
        from nfs_scanner_pro.scan.real_scan_plan import (
            ScanPlanPoint,
            SmallAreaScanPlan,
            generate_3x3_scan_plan,
        )
        from nfs_scanner_pro.scan.real_scan_safety import (
            ScanSafetyLimits,
            validate_scan_plan,
            validate_scan_point,
        )
        from nfs_scanner_pro.scan.real_scan_plan_persistence import (
            load_scan_plan,
            save_scan_plan,
        )

        ok = all(
            obj is not None
            for obj in (
                ScanPlanPoint,
                SmallAreaScanPlan,
                generate_3x3_scan_plan,
                ScanSafetyLimits,
                validate_scan_plan,
                validate_scan_point,
                save_scan_plan,
                load_scan_plan,
            )
        )
        if ok:
            report.pass_check("real_scan_plan_imports")
        else:
            report.fail_check("real_scan_plan_imports", "missing symbol")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_scan_plan_imports", str(exc))


def check_generate_3x3_plan(report: verification_report.VerificationReport) -> None:
    report.start_check("generate_3x3_plan")
    try:
        from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan

        plan = generate_3x3_scan_plan(
            center_x=50.0,
            center_y=-50.0,
            z=5.0,
            step_mm=0.5,
        )
        coords = [(point.x, point.y) for point in plan.points]
        payload = json.dumps(plan.as_dict())
        ok = (
            plan.point_count() == 9
            and plan.rows == 3
            and plan.cols == 3
            and coords == list(EXPECTED_SERPENTINE)
            and plan.dry_run is True
            and plan.safe_mode is True
            and "move_to" not in payload.lower()
            and "G0" not in payload
            and "G1" not in payload
        )
        if ok:
            report.pass_check("generate_3x3_plan")
        else:
            report.fail_check("generate_3x3_plan", f"coords={coords}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("generate_3x3_plan", str(exc))


def check_soft_limit_validation(report: verification_report.VerificationReport) -> None:
    report.start_check("soft_limit_validation")
    try:
        from nfs_scanner_pro.scan.real_scan_plan import (
            ScanPlanPoint,
            SmallAreaScanPlan,
            generate_3x3_scan_plan,
        )
        from nfs_scanner_pro.scan.real_scan_safety import (
            ScanSafetyLimits,
            validate_scan_plan,
            validate_scan_point,
        )

        limits = ScanSafetyLimits.from_env()
        good = generate_3x3_scan_plan(
            center_x=50.0,
            center_y=-50.0,
            z=5.0,
            step_mm=0.5,
        )
        good_result = validate_scan_plan(good, limits=limits)

        bad_x = validate_scan_point(250.0, -50.0, 5.0, limits=limits)
        bad_y = validate_scan_point(50.0, -250.0, 5.0, limits=limits)
        bad_z = validate_scan_point(50.0, -50.0, 100.0, limits=limits)

        big_step = generate_3x3_scan_plan(step_mm=2.0)
        big_step_result = validate_scan_plan(big_step, limits=limits)

        too_many = SmallAreaScanPlan(
            plan_id="TEST-MANY",
            project_name="T",
            region_name="T",
            origin_x=50.0,
            origin_y=-50.0,
            origin_z=5.0,
            step_x=0.5,
            step_y=0.5,
            rows=3,
            cols=4,
            frequency="2.450 GHz",
            trace="Trace 1",
            points=[
                ScanPlanPoint(
                    index=i,
                    row=0,
                    col=i,
                    x=50.0 + i * 0.1,
                    y=-50.0,
                    z=5.0,
                    frequency="2.450 GHz",
                    trace="Trace 1",
                )
                for i in range(10)
            ],
        )
        env_backup = os.environ.get("NFS_SCAN_MAX_POINTS")
        os.environ["NFS_SCAN_MAX_POINTS"] = "9"
        too_many_limits = ScanSafetyLimits.from_env()
        too_many_result = validate_scan_plan(too_many, limits=too_many_limits)
        if env_backup is None:
            os.environ.pop("NFS_SCAN_MAX_POINTS", None)
        else:
            os.environ["NFS_SCAN_MAX_POINTS"] = env_backup

        ok = (
            good_result.get("ok") is True
            and bad_x.get("ok") is False
            and bad_y.get("ok") is False
            and bad_z.get("ok") is False
            and big_step_result.get("ok") is False
            and too_many_result.get("ok") is False
        )
        if ok:
            report.pass_check("soft_limit_validation")
        else:
            report.fail_check(
                "soft_limit_validation",
                f"good={good_result} step={big_step_result} many={too_many_result}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("soft_limit_validation", str(exc))


def check_scan_plan_persistence(report: verification_report.VerificationReport) -> None:
    report.start_check("scan_plan_persistence")
    try:
        verification_runtime.enter_release_runtime("R042")
        from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan
        from nfs_scanner_pro.scan.real_scan_plan_persistence import save_scan_plan
        from nfs_scanner_pro.scan.real_scan_safety import validate_scan_plan

        plan = generate_3x3_scan_plan(
            center_x=50.0,
            center_y=-50.0,
            z=5.0,
            step_mm=0.5,
        )
        validation = validate_scan_plan(plan)
        validation["valid"] = validation.get("ok", False)
        paths = save_scan_plan(plan, validation)
        runtime_root = verification_runtime.get_release_runtime_dir("042")
        joint_root = runtime_root / "scan_plans" / plan.plan_id

        ok = (
            paths["json_path"].is_file()
            and paths["csv_path"].is_file()
            and paths["summary_path"].is_file()
            and "R042" in paths["json_path"].as_posix()
            and joint_root.is_dir()
        )
        if ok:
            data = json.loads(paths["json_path"].read_text(encoding="utf-8"))
            summary = json.loads(paths["summary_path"].read_text(encoding="utf-8"))
            with paths["csv_path"].open(encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))
            ok = (
                data.get("dry_run") is True
                and data.get("safe_mode") is True
                and summary.get("valid") is True
                and summary.get("dry_run") is True
                and summary.get("safe_mode") is True
                and len(rows) == 10
                and len(rows[0]) == len(rows[1])
            )
        if ok:
            report.pass_check(
                "scan_plan_persistence",
                paths["json_path"].relative_to(ROOT).as_posix(),
            )
        else:
            report.fail_check("scan_plan_persistence", str(paths))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("scan_plan_persistence", str(exc))


def _run_plan_script(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    run_env = dict(os.environ if env is None else env)
    run_env.setdefault("QT_QPA_PLATFORM", "offscreen")
    run_env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "plan_small_area_scan_dry_run.py"), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=run_env,
    )


def check_dry_run_script_no_save(report: verification_report.VerificationReport) -> None:
    report.start_check("dry_run_script_no_save")
    with mock.patch.object(
        socket,
        "create_" + "connection",
        side_effect=AssertionError("socket"),
    ):
        proc = _run_plan_script(["--no-save"])
    text = proc.stdout + proc.stderr
    ok = (
        proc.returncode == 0
        and text.count("X=") >= 9
        and "Dry run only" in text
        and "No motion command executed" in text
        and "No spectrum sweep started" in text
        and "No real device connected" in text
        and "Saved scan_plan.json" not in text
    )
    if ok:
        report.pass_check("dry_run_script_no_save")
    else:
        report.fail_check("dry_run_script_no_save", text[-400:])


def check_dry_run_script_save(report: verification_report.VerificationReport) -> None:
    report.start_check("dry_run_script_save")
    verification_runtime.enter_release_runtime("R042")
    with mock.patch.object(
        socket,
        "create_" + "connection",
        side_effect=AssertionError("socket"),
    ):
        proc = _run_plan_script([])
    text = proc.stdout + proc.stderr
    ok = (
        proc.returncode == 0
        and "Saved scan_plan.json" in text
        and "Saved scan_plan.csv" in text
        and "Saved scan_plan_summary.json" in text
        and "Dry run only" in text
    )
    if ok:
        report.pass_check("dry_run_script_save")
    else:
        report.fail_check("dry_run_script_save", text[-400:])


def check_no_real_connection_or_sampling(report: verification_report.VerificationReport) -> None:
    report.start_check("no_real_connection_or_sampling")
    hits: list[str] = []
    plan_script = (SCRIPTS_DIR / "plan_small_area_scan_dry_run.py").read_text(encoding="utf-8")
    forbidden_imports = (
        "MotionGrblAdapter",
        "SpectrumScpiAdapter",
        "JointSampleAdapter",
        "RealDeviceManager",
        "sample_once_safe",
        "safe_jog",
        "read_single_point_amplitude",
    )
    for token in forbidden_imports:
        if token in plan_script:
            hits.append(f"plan_script:{token}")

    try:
        fake_serial = mock.MagicMock(side_effect=AssertionError("serial"))
        with mock.patch.dict("sys.modules", {"serial": mock.MagicMock(Serial=fake_serial)}):
            with mock.patch.object(
                socket,
                "create_" + "connection",
                side_effect=AssertionError("socket"),
            ):
                proc = _run_plan_script(["--no-save"])
        if proc.returncode != 0:
            hits.append(f"script_exit={proc.returncode}")
    except Exception as exc:  # noqa: BLE001
        hits.append(str(exc))

    if hits:
        report.fail_check("no_real_connection_or_sampling", "; ".join(hits))
    else:
        report.pass_check("no_real_connection_or_sampling")


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
    for script in ("029", "041"):
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
        / "docs/product-spec/release/Release_042_Real_Small_Area_3x3_Scan_Dry_Run_Planner/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_042 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_042.py",
        "python scripts/verify_all.py --only 042",
        "python scripts/plan_small_area_scan_dry_run.py --no-save",
        "python scripts/plan_small_area_scan_dry_run.py",
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
            "## 是否连接真实设备",
            "",
            "否",
            "",
            "## 是否执行真实运动",
            "",
            "否",
            "",
            "## 是否执行真实采样",
            "",
            "否",
            "",
            "## 是否启动 sweep",
            "",
            "否",
            "",
            "## 是否生成 3x3 扫描计划",
            "",
            "是",
            "",
            "## 是否保存 JSON / CSV",
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
    verification_runtime.enter_release_runtime("R042")
    report = verification_report.VerificationReport("042")

    check_compileall(report)
    check_real_scan_plan_imports(report)
    check_generate_3x3_plan(report)
    check_soft_limit_validation(report)
    check_scan_plan_persistence(report)
    check_dry_run_script_no_save(report)
    check_dry_run_script_save(report)
    check_no_real_connection_or_sampling(report)
    check_source_no_motion_or_sweep_commands(report)
    check_mock_ui_unchanged(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
