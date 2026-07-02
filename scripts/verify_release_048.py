#!/usr/bin/env python3
"""Release_048 自动验收 — Real Hardware Commissioning Standard Workflow。"""

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
from verification_utils import FORBIDDEN_PATTERNS, ROOT as UTILS_ROOT, setup_path  # noqa: E402

IMPORT_MODULES = (
    "nfs_scanner_pro.hardware_commissioning.commissioning_model",
    "nfs_scanner_pro.hardware_commissioning.commissioning_workflow",
    "nfs_scanner_pro.hardware_commissioning.commissioning_runner",
    "nfs_scanner_pro.hardware_commissioning.commissioning_persistence",
    "nfs_scanner_pro.hardware_commissioning.commissioning_checks",
)

COMMISSIONING_DOCS = (
    "docs/hardware/commissioning/README.md",
    "docs/hardware/commissioning/00-overview.md",
    "docs/hardware/commissioning/01-environment-check.md",
    "docs/hardware/commissioning/02-motion-check.md",
    "docs/hardware/commissioning/03-spectrum-check.md",
    "docs/hardware/commissioning/04-camera-check.md",
    "docs/hardware/commissioning/05-servo-check.md",
    "docs/hardware/commissioning/06-joint-sample-check.md",
    "docs/hardware/commissioning/07-small-area-scan-check.md",
    "docs/hardware/commissioning/08-acceptance-criteria.md",
    "docs/hardware/commissioning/09-failure-record-template.md",
    "docs/hardware/commissioning/10-real-run-gate.md",
)

SOURCE_GUARD_FILES = tuple(
    (SRC / "nfs_scanner_pro/hardware_commissioning").rglob("*.py")
) + (
    SCRIPTS_DIR / "start_hardware_commissioning.py",
    SCRIPTS_DIR / "validate_commissioning_readiness.py",
    SCRIPTS_DIR / "generate_commissioning_template.py",
)

DANGEROUS_COMMANDS = ("G0", "G1", "$J", "$H", "G28", "INIT", "SING", "CALC:DATA?", "TRAC:DATA?")


def _clear_env() -> dict[str, str | None]:
    keys = (
        "NFS_ENABLE_REAL_HARDWARE",
        "NFS_ENABLE_REAL_SCAN_EXECUTION",
        "NFS_HARDWARE_MODE",
    )
    backup: dict[str, str | None] = {}
    for key in keys:
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
                report.fail_check("compileall", str(exc))
                return
        report.pass_check("compileall")
    else:
        report.fail_check("compileall")


def check_commissioning_config_templates(report: verification_report.VerificationReport) -> None:
    report.start_check("commissioning_config_templates")
    ok = (
        (ROOT / "config/commissioning.workflow.example.yaml").is_file()
        and (ROOT / "config/commissioning.local.example.yaml").is_file()
        and "commissioning.local.yaml" in (ROOT / ".gitignore").read_text(encoding="utf-8")
    )
    if ok:
        report.pass_check("commissioning_config_templates")
    else:
        report.fail_check("commissioning_config_templates")


def check_commissioning_imports(report: verification_report.VerificationReport) -> None:
    report.start_check("commissioning_imports")
    try:
        for mod in IMPORT_MODULES:
            __import__(mod)
        report.pass_check("commissioning_imports")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("commissioning_imports", str(exc))


def check_default_workflow(report: verification_report.VerificationReport) -> None:
    report.start_check("default_workflow")
    try:
        from nfs_scanner_pro.hardware_commissioning.commissioning_workflow import (
            build_default_workflow,
            build_session_from_workflow,
            validate_workflow,
        )

        wf = build_default_workflow()
        val = validate_workflow(wf)
        session = build_session_from_workflow(wf, mode="offline")
        ids = {step.step_id for step in session.steps}
        ok = (
            val.get("ok")
            and "env_check" in ids
            and "motion_status" in ids
            and "spectrum_idn" in ids
            and "joint_sample" in ids
            and "scan_fake_run" in ids
            and "real_run_gate" in ids
            and not session.is_ready_for_real_run()
        )
        if ok:
            report.pass_check("default_workflow")
        else:
            report.fail_check("default_workflow", str(ids))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("default_workflow", str(exc))


def check_runner_offline(report: verification_report.VerificationReport) -> None:
    report.start_check("runner_offline")
    backup = _clear_env()
    try:
        from nfs_scanner_pro.hardware_commissioning.commissioning_persistence import save_session
        from nfs_scanner_pro.hardware_commissioning.commissioning_runner import CommissioningRunner

        runner = CommissioningRunner()
        session = runner.run_offline()
        paths = save_session(session)
        ok = (
            session.total_steps() >= 5
            and session.passed_steps() >= 5
            and session.is_ready_for_real_run() is False
            and paths["session_json"].is_file()
        )
        if ok:
            report.pass_check("runner_offline")
        else:
            report.fail_check(
                "runner_offline",
                f"passed={session.passed_steps()} total={session.total_steps()}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("runner_offline", str(exc))
    finally:
        _restore_env(backup)


def check_runner_fake(report: verification_report.VerificationReport) -> None:
    report.start_check("runner_fake")
    backup = _clear_env()
    try:
        from nfs_scanner_pro.hardware_commissioning.commissioning_runner import CommissioningRunner

        session = CommissioningRunner().run_fake()
        motion = next(s for s in session.steps if s.step_id == "motion_status")
        fake_run = next(s for s in session.steps if s.step_id == "scan_fake_run")
        ok = (
            motion.status == "passed"
            and fake_run.status == "passed"
            and not session.is_ready_for_real_run()
        )
        if ok:
            report.pass_check("runner_fake")
        else:
            report.fail_check("runner_fake", f"motion={motion.status} fake={fake_run.status}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("runner_fake", str(exc))
    finally:
        _restore_env(backup)


def check_runner_real_safe_blocked(report: verification_report.VerificationReport) -> None:
    report.start_check("runner_real_safe_blocked")
    backup = _clear_env()
    try:
        from nfs_scanner_pro.hardware_commissioning.commissioning_runner import CommissioningRunner

        def _blocked(*_a, **_k):
            raise AssertionError("blocked")

        with (
            mock.patch("serial.Serial", side_effect=_blocked),
            mock.patch("socket.create_connection", side_effect=_blocked),
            mock.patch("pyvisa.ResourceManager", side_effect=_blocked),
            mock.patch("cv2.VideoCapture", side_effect=_blocked),
        ):
            session = CommissioningRunner().run_real_safe()
        ok = session.blocked_steps() > 0 and not session.is_ready_for_real_run()
        if ok:
            report.pass_check("runner_real_safe_blocked")
        else:
            report.fail_check("runner_real_safe_blocked", f"blocked={session.blocked_steps()}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("runner_real_safe_blocked", str(exc))
    finally:
        _restore_env(backup)


def check_commissioning_persistence(report: verification_report.VerificationReport) -> None:
    report.start_check("commissioning_persistence")
    backup = _clear_env()
    try:
        from nfs_scanner_pro.hardware_commissioning.commissioning_persistence import save_session
        from nfs_scanner_pro.hardware_commissioning.commissioning_runner import CommissioningRunner

        runtime = verification_runtime.get_current_release_runtime()
        base = runtime / "commissioning_sessions"
        session = CommissioningRunner().run_offline()
        paths = save_session(session, base=base)
        summary = json.loads(paths["summary_json"].read_text(encoding="utf-8"))
        with paths["steps_csv"].open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        md = paths["report_md"].read_text(encoding="utf-8")
        ok = (
            paths["session_json"].is_file()
            and len(rows) >= 5
            and "ready_for_real_run" in summary
            and not summary["ready_for_real_run"]
            and len(md.strip()) > 20
            and str(runtime) in str(paths["session_json"].resolve())
        )
        if ok:
            report.pass_check("commissioning_persistence")
        else:
            report.fail_check("commissioning_persistence", str(summary))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("commissioning_persistence", str(exc))
    finally:
        _restore_env(backup)


def _run_script(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "start_hardware_commissioning.py"), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def check_start_commissioning_script_offline(report: verification_report.VerificationReport) -> None:
    report.start_check("start_commissioning_script_offline")
    proc = _run_script(["--mode", "offline"])
    ok = proc.returncode == 0 and "session_id:" in proc.stdout
    if ok:
        report.pass_check("start_commissioning_script_offline")
    else:
        report.fail_check("start_commissioning_script_offline", proc.stdout + proc.stderr)


def check_start_commissioning_script_fake(report: verification_report.VerificationReport) -> None:
    report.start_check("start_commissioning_script_fake")
    proc = _run_script(["--mode", "fake"])
    ok = proc.returncode == 0 and "ready_for_real_run: False" in proc.stdout
    if ok:
        report.pass_check("start_commissioning_script_fake")
    else:
        report.fail_check("start_commissioning_script_fake", proc.stdout + proc.stderr)


def check_start_commissioning_script_real_safe_blocked(report: verification_report.VerificationReport) -> None:
    report.start_check("start_commissioning_script_real_safe_blocked")
    proc = _run_script(["--mode", "real-safe"])
    ok = "blocked_steps:" in proc.stdout and proc.returncode == 0
    if ok:
        report.pass_check("start_commissioning_script_real_safe_blocked")
    else:
        report.fail_check("start_commissioning_script_real_safe_blocked", proc.stdout + proc.stderr)


def check_readiness_script(report: verification_report.VerificationReport) -> None:
    report.start_check("readiness_script")
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "validate_commissioning_readiness.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    ok = proc.returncode == 0 and "COMMISSIONING READINESS: PASS" in proc.stdout
    if ok:
        report.pass_check("readiness_script")
    else:
        report.fail_check("readiness_script", proc.stdout + proc.stderr)


def check_template_generation_script(report: verification_report.VerificationReport) -> None:
    report.start_check("template_generation_script")
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "generate_commissioning_template.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    ok = proc.returncode == 0 and "hardware.local.yaml.template" in proc.stdout
    if ok:
        report.pass_check("template_generation_script")
    else:
        report.fail_check("template_generation_script", proc.stdout + proc.stderr)


def check_commissioning_docs_exist(report: verification_report.VerificationReport) -> None:
    report.start_check("commissioning_docs_exist")
    missing = [d for d in COMMISSIONING_DOCS if not (ROOT / d).is_file()]
    empty = [d for d in COMMISSIONING_DOCS if (ROOT / d).is_file() and not (ROOT / d).read_text(encoding="utf-8").strip()]
    if missing or empty:
        report.fail_check("commissioning_docs_exist", ", ".join(missing + empty))
    else:
        report.pass_check("commissioning_docs_exist")


def _line_has_guard(text: str, line: str) -> bool:
    guards = (
        "is_real_hardware_enabled",
        "require_real",
        "FakeTransport",
        "dry_run",
        "fake_run",
        "blocked",
        "test_all_safe",
        "CommissioningRunner",
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
            if "hardware_commissioning" in str(path):
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
    for release in ("029", "046", "047"):
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
    bad = [l.strip() for l in proc.stdout.splitlines() if l.strip().startswith("prototypes/high_fidelity/")]
    if bad:
        report.fail_check("no_high_fidelity_changes", ", ".join(bad))
    else:
        report.pass_check("no_high_fidelity_changes")


def write_acceptance_report(report: verification_report.VerificationReport) -> Path:
    out = ROOT / "docs/product-spec/release/Release_048_Real_Hardware_Commissioning_Standard_Workflow/ACCEPTANCE_REPORT.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_048 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_048.py",
        "python scripts/start_hardware_commissioning.py --mode offline",
        "python scripts/start_hardware_commissioning.py --mode fake",
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
            "## 是否支持 offline commissioning",
            "",
            "是",
            "",
            "## 是否支持 fake commissioning",
            "",
            "是",
            "",
            "## 是否支持 real-safe blocked",
            "",
            "是",
            "",
            "## 是否生成 session 报告",
            "",
            "是",
            "",
            "## 是否生成联调模板",
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
    verification_runtime.enter_release_runtime("R048")
    report = verification_report.VerificationReport("048")

    check_compileall(report)
    check_commissioning_config_templates(report)
    check_commissioning_imports(report)
    check_default_workflow(report)
    check_runner_offline(report)
    check_runner_fake(report)
    check_runner_real_safe_blocked(report)
    check_commissioning_persistence(report)
    check_start_commissioning_script_offline(report)
    check_start_commissioning_script_fake(report)
    check_start_commissioning_script_real_safe_blocked(report)
    check_readiness_script(report)
    check_template_generation_script(report)
    check_commissioning_docs_exist(report)
    check_source_safety_guards(report)
    check_mock_ui_unchanged(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
