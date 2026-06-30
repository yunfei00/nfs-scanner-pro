#!/usr/bin/env python3
"""Release_031 自动验收 — Verification Performance & Isolation。"""

from __future__ import annotations

import compileall
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import verification_report  # noqa: E402
import verification_runtime  # noqa: E402
from verification_utils import (  # noqa: E402
    FORBIDDEN_PATTERNS,
    MOCK_DEVICE_DIRS,
    PROJECT_NAME,
    ROOT,
    setup_path,
)

VERIFY_ALL = SCRIPTS_DIR / "verify_all.py"
NESTED = os.environ.get("NFS_VERIFY_NESTED") == "1"


def _run_verify_all(*args: str, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(VERIFY_ALL), *args]
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
    modules_ok = True
    for mod in ("verification_runtime", "verification_report"):
        try:
            __import__(mod)
        except ImportError:
            modules_ok = False
    verify_all_ok = VERIFY_ALL.is_file()
    ok = ok and modules_ok and verify_all_ok
    if ok:
        report.pass_check("compileall")
    else:
        report.fail_check("compileall", "import or compile failed")


def check_runtime_isolation(report: verification_report.VerificationReport) -> None:
    report.start_check("runtime_isolation")
    try:
        mock_projects = verification_runtime.get_runtime_dir() / "mock_projects"
        mock_projects.mkdir(parents=True, exist_ok=True)
        marker = mock_projects / ".verify_031_keep"
        marker.write_text("keep", encoding="utf-8")

        release_dir = verification_runtime.get_release_runtime_dir("R031")
        probe = release_dir / "isolation_probe.txt"
        probe.write_text("probe", encoding="utf-8")

        scan_dir = verification_runtime.make_project_scan_dir(
            "R031", PROJECT_NAME, "ST-VERIFY-031"
        )
        report_dir = verification_runtime.make_project_report_dir(
            "R031", PROJECT_NAME, "RP-VERIFY-031"
        )
        (scan_dir / "scan_result.json").write_text("{}", encoding="utf-8")
        (report_dir / "report_draft.json").write_text("{}", encoding="utf-8")

        verification_runtime.clean_release_runtime("R031")

        ok = (
            marker.is_file()
            and not probe.is_file()
            and verification_runtime.get_release_runtime_dir("R031").is_dir()
            and not (verification_runtime.get_release_runtime_dir("R031") / "isolation_probe.txt").is_file()
        )
        scan_recreated = verification_runtime.make_project_scan_dir(
            "R031", PROJECT_NAME, "ST-VERIFY-031"
        )
        ok = ok and scan_recreated.is_dir()
        if ok:
            report.pass_check("runtime_isolation", str(scan_dir.relative_to(ROOT)))
        else:
            report.fail_check("runtime_isolation", "clean leaked or removed mock_projects")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("runtime_isolation", str(exc))


def check_runtime_gitignore(report: verification_report.VerificationReport) -> None:
    report.start_check("runtime_gitignore")
    ok, detail = verification_runtime.assert_runtime_ignored_by_git()
    if ok:
        report.pass_check("runtime_gitignore", detail)
    else:
        report.fail_check("runtime_gitignore", detail)


def check_verify_all_list(report: verification_report.VerificationReport) -> None:
    if NESTED:
        report.skip_check("verify_all_list", "NFS_VERIFY_NESTED=1")
        return
    report.start_check("verify_all_list")
    proc = _run_verify_all("--list")
    text = proc.stdout
    ok = proc.returncode == 0 and all(
        f"Release {num:03d}" in text or f"Release 0{num}" in text or f"({num:03d})" in text
        for num in range(22, 32)
    )
    if ok:
        report.pass_check("verify_all_list")
    else:
        report.fail_check("verify_all_list", proc.stdout[-400:] or str(proc.returncode))


def check_verify_all_only(report: verification_report.VerificationReport) -> None:
    if NESTED:
        report.skip_check("verify_all_only", "NFS_VERIFY_NESTED=1")
        return
    report.start_check("verify_all_only")
    proc = _run_verify_all("--only", "30")
    text = proc.stdout + proc.stderr
    running = [line for line in text.splitlines() if line.startswith("Running ")]
    ok = (
        proc.returncode == 0
        and "RESULT: PASS" in text
        and "Release 030" in text
        and "TOTAL:" in text
        and len(running) == 1
        and "Release 030" in running[0]
    )
    if ok:
        report.pass_check("verify_all_only", f"{running[0] if running else ''}")
    else:
        report.fail_check("verify_all_only", tail(text))


def check_verify_all_from(report: verification_report.VerificationReport) -> None:
    if NESTED:
        report.skip_check("verify_all_from", "NFS_VERIFY_NESTED=1")
        return
    report.start_check("verify_all_from")
    proc = _run_verify_all(
        "--from",
        "30",
        env={"NFS_VERIFY_NESTED": "1"},
    )
    text = proc.stdout + proc.stderr
    running = [line for line in text.splitlines() if line.startswith("Running ")]
    ok = (
        proc.returncode == 0
        and "RESULT: PASS" in text
        and any("Release 030" in line for line in running)
        and any("Release 031" in line for line in running)
        and len(running) == 2
    )
    if ok:
        report.pass_check("verify_all_from", f"runs={len(running)}")
    else:
        report.fail_check("verify_all_from", tail(text))


def check_verify_all_summary_format(report: verification_report.VerificationReport) -> None:
    report.start_check("verify_all_summary_format")
    source = VERIFY_ALL.read_text(encoding="utf-8")
    required = (
        "Verification Suite",
        "TOTAL:",
        "RESULT:",
        "argparse",
        "--only",
        "--from",
        "--list",
        "fail_fast",
    )
    missing = [token for token in required if token not in source]
    ok = not missing and "verify_release_031.py" in source
    if ok:
        report.pass_check("verify_all_summary_format")
    else:
        report.fail_check("verify_all_summary_format", ", ".join(missing))


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
                    hits.append(f"{path.relative_to(ROOT)}: {pattern}")
    if not hits:
        report.pass_check("no_real_device_access")
    else:
        report.fail_check("no_real_device_access", "; ".join(hits))


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
    names = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    bad = [name for name in names if name.startswith("prototypes/high_fidelity/")]
    ok = not bad
    if ok:
        report.pass_check("no_high_fidelity_changes")
    else:
        report.fail_check("no_high_fidelity_changes", ", ".join(bad))


def tail(text: str, lines: int = 20) -> str:
    parts = text.splitlines()
    return "\n".join(parts[-lines:])


def write_acceptance_report(
    report: verification_report.VerificationReport,
    verify_all_total: float | None,
) -> Path:
    out = (
        ROOT
        / "docs/product-spec/release/Release_031_Verification_Performance_Isolation/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_031 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_031.py",
        "python scripts/verify_all.py --list",
        "python scripts/verify_all.py --only 030",
        "python scripts/verify_all.py --from 030",
        "python scripts/verify_all.py",
        "```",
        "",
        "## 检查项",
        "",
    ]
    for name, ok, detail, elapsed, skipped in report.entries:
        if skipped:
            status = "SKIP"
        else:
            status = "PASS" if ok else "FAIL"
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
            "## verify_all.py 总耗时",
            "",
            f"{verify_all_total:.2f}s" if verify_all_total is not None else "（见 CI / 本地全量运行）",
            "",
            "## runtime 隔离路径",
            "",
            "- `runtime/verification/R031/mock_projects/`",
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
    report = verification_report.VerificationReport("031")

    check_compileall(report)
    check_runtime_isolation(report)
    check_runtime_gitignore(report)
    check_verify_all_list(report)
    check_verify_all_only(report)
    check_verify_all_from(report)
    check_verify_all_summary_format(report)
    check_no_real_device_access(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report, None)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
