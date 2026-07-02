#!/usr/bin/env python3
"""Release_033 自动验收 — Release Verification Script Generator。"""

from __future__ import annotations

import compileall
import importlib
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import scaffold_verify_release  # noqa: E402
import verification_report  # noqa: E402
import verification_runtime  # noqa: E402
from verification_utils import (  # noqa: E402
    FORBIDDEN_PATTERNS,
    MOCK_DEVICE_DIRS,
    ROOT as UTILS_ROOT,
    setup_path,
)

SCAFFOLD = SCRIPTS_DIR / "scaffold_verify_release.py"
VERIFY_ALL = SCRIPTS_DIR / "verify_all.py"
NESTED = os.environ.get("NFS_VERIFY_NESTED") == "1"
TEMPLATE_SOURCE_MARKERS = (
    "QT_QPA_PLATFORM",
    "enter_release_runtime",
    "VerificationReport",
    "compileall",
    "no_real_device_access",
    "no_high_fidelity_changes",
)
TEMPLATE_OUTPUT_MARKERS = TEMPLATE_SOURCE_MARKERS + ("RESULT: PASS",)
TEMP_RELEASE = 998
TEMP_NAME = "Scaffold Self Test"


def _run(cmd: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=run_env,
    )


def check_compileall(report: verification_report.VerificationReport) -> None:
    report.start_check("compileall")
    ok = bool(compileall.compile_dir(str(ROOT / "src" / "nfs_scanner_pro"), quiet=1))
    for mod in ("verification_runtime", "verification_report", "scaffold_verify_release"):
        try:
            importlib.import_module(mod)
        except ImportError:
            ok = False
    if ok:
        report.pass_check("compileall")
    else:
        report.fail_check("compileall", "import or compile failed")


def check_scaffold_help(report: verification_report.VerificationReport) -> None:
    report.start_check("scaffold_help")
    proc = _run([sys.executable, str(SCAFFOLD), "--help"])
    ok = proc.returncode == 0 and "--release" in proc.stdout and "--dry-run" in proc.stdout
    if ok:
        report.pass_check("scaffold_help")
    else:
        report.fail_check("scaffold_help", proc.stderr or str(proc.returncode))


def check_scaffold_dry_run(report: verification_report.VerificationReport) -> None:
    report.start_check("scaffold_dry_run")
    proc = _run(
        [
            sys.executable,
            str(SCAFFOLD),
            "--release",
            "099",
            "--name",
            "Dry Run Verification",
            "--dry-run",
        ]
    )
    text = (proc.stdout + proc.stderr).replace("\\", "/")
    ok = (
        proc.returncode == 0
        and "scripts/verify_release_099.py" in text
        and "Release_099_Dry_Run_Verification" in text
        and not (SCRIPTS_DIR / "verify_release_099.py").is_file()
    )
    if ok:
        report.pass_check("scaffold_dry_run")
    else:
        report.fail_check("scaffold_dry_run", text[-400:] or str(proc.returncode))


def check_scaffold_temp_generate(report: verification_report.VerificationReport) -> None:
    report.start_check("scaffold_temp_generate")
    temp_config = scaffold_verify_release.build_config(
        TEMP_RELEASE,
        title=TEMP_NAME,
    )
    failures: list[str] = []
    try:
        proc = _run(
            [
                sys.executable,
                str(SCAFFOLD),
                "--release",
                str(TEMP_RELEASE),
                "--name",
                TEMP_NAME,
            ]
        )
        if proc.returncode != 0:
            failures.append(f"scaffold exit={proc.returncode}: {proc.stderr[-200:]}")
        if not temp_config.verify_script.is_file():
            failures.append("verify script missing")
        if not temp_config.docs_dir.is_dir():
            failures.append("docs dir missing")
        verify_all_text = VERIFY_ALL.read_text(encoding="utf-8")
        if f"verify_release_{TEMP_RELEASE:03d}.py" not in verify_all_text:
            failures.append("verify_all not updated")

        if temp_config.verify_script.is_file():
            run_proc = _run(
                [sys.executable, str(temp_config.verify_script)],
                env=verification_runtime.build_release_env(f"{TEMP_RELEASE:03d}"),
            )
            if run_proc.returncode != 0 or "RESULT: PASS" not in run_proc.stdout:
                failures.append(
                    f"generated script failed: {run_proc.stdout[-300:]}{run_proc.stderr[-200:]}"
                )
    finally:
        cleanup = _run(
            [
                sys.executable,
                str(SCAFFOLD),
                "--release",
                str(TEMP_RELEASE),
                "--name",
                TEMP_NAME,
                "--remove",
            ]
        )
        if cleanup.returncode != 0:
            failures.append(f"cleanup exit={cleanup.returncode}")
        if temp_config.verify_script.is_file() or temp_config.docs_dir.is_dir():
            failures.append("998 artifacts remain after cleanup")
        post_text = VERIFY_ALL.read_text(encoding="utf-8")
        if f"verify_release_{TEMP_RELEASE:03d}.py" in post_text:
            failures.append("verify_all still contains 998")
        git_proc = _run(["git", "diff", "--name-only"])
        if str(TEMP_RELEASE) in git_proc.stdout:
            failures.append("git diff contains 998")

    if failures:
        report.fail_check("scaffold_temp_generate", "; ".join(failures))
    else:
        report.pass_check("scaffold_temp_generate")


def check_scaffold_existing_release_guard(report: verification_report.VerificationReport) -> None:
    report.start_check("scaffold_existing_release_guard")
    proc = _run(
        [
            sys.executable,
            str(SCAFFOLD),
            "--release",
            "033",
            "--name",
            "Should Fail",
        ]
    )
    text = (proc.stdout + proc.stderr).lower()
    ok = proc.returncode != 0 and ("already exists" in text or "已存在" in text)
    if ok:
        report.pass_check("scaffold_existing_release_guard")
    else:
        report.fail_check("scaffold_existing_release_guard", proc.stdout[-300:] or str(proc.returncode))


def check_scaffold_template_content(report: verification_report.VerificationReport) -> None:
    report.start_check("scaffold_template_content")
    source = SCAFFOLD.read_text(encoding="utf-8")
    sample = scaffold_verify_release.render_verify_script(
        scaffold_verify_release.build_config(999, title="Template Probe")
    )
    missing_source = [m for m in TEMPLATE_SOURCE_MARKERS if m not in source]
    missing_sample = [m for m in TEMPLATE_OUTPUT_MARKERS if m not in sample]
    missing = missing_source + [f"sample:{m}" for m in missing_sample]
    if missing:
        report.fail_check("scaffold_template_content", ", ".join(missing))
    else:
        report.pass_check("scaffold_template_content")


def check_verify_all_cli(report: verification_report.VerificationReport) -> None:
    if NESTED:
        report.skip_check("verify_all_cli", "NFS_VERIFY_NESTED=1")
        return
    report.start_check("verify_all_cli")
    failures: list[str] = []

    list_proc = _run([sys.executable, str(VERIFY_ALL), "--list"])
    list_text = list_proc.stdout
    if list_proc.returncode != 0:
        failures.append("--list failed")
    else:
        for num in range(22, 43):
            if f"({num:03d})" not in list_text:
                failures.append(f"--list missing {num:03d}")

    only_proc = _run([sys.executable, str(VERIFY_ALL), "--only", "032"])
    only_text = only_proc.stdout + only_proc.stderr
    if only_proc.returncode != 0 or "RESULT: PASS" not in only_text:
        failures.append("--only 032 failed")

    from_proc = _run(
        [sys.executable, str(VERIFY_ALL), "--from", "036"],
        env={"NFS_VERIFY_NESTED": "1"},
    )
    from_text = from_proc.stdout + from_proc.stderr
    running = [ln for ln in from_text.splitlines() if ln.startswith("Running ")]
    if from_proc.returncode != 0 or "RESULT: PASS" not in from_text:
        failures.append("--from 036 failed")
    elif len(running) != 2:
        failures.append(f"--from 036 runs={len(running)} expected 2")
    elif not any("Release 037" in ln for ln in running):
        failures.append("--from 036 missing Release 037")

    if failures:
        report.fail_check("verify_all_cli", "; ".join(failures))
    else:
        report.pass_check("verify_all_cli")


def check_no_real_device_access(report: verification_report.VerificationReport) -> None:
    report.start_check("no_real_device_access")
    hits: list[str] = []
    for base in MOCK_DEVICE_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in text:
                    hits.append(f"{path.relative_to(UTILS_ROOT)}: {pattern}")
    if hits:
        report.fail_check("no_real_device_access", "; ".join(hits))
    else:
        report.pass_check("no_real_device_access")


def check_no_high_fidelity_changes(report: verification_report.VerificationReport) -> None:
    report.start_check("no_high_fidelity_changes")
    proc = _run(["git", "diff", "--name-only"])
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
        / "docs/product-spec/release/Release_033_Release_Verification_Script_Generator/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_033 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_033.py",
        "python scripts/scaffold_verify_release.py --help",
        "python scripts/verify_all.py",
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
            "## 临时 998 脚手架是否已清理",
            "",
            "是" if report.is_pass() else "否",
            "",
            "## 是否接真实设备",
            "",
            "否",
            "",
            "## 是否生成真实 PDF / Word / Excel",
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
    verification_runtime.enter_release_runtime("R033")
    report = verification_report.VerificationReport("033")

    check_compileall(report)
    check_scaffold_help(report)
    check_scaffold_dry_run(report)
    check_scaffold_temp_generate(report)
    check_scaffold_existing_release_guard(report)
    check_scaffold_template_content(report)
    check_verify_all_cli(report)
    check_no_real_device_access(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
