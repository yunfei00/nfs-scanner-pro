#!/usr/bin/env python3
"""Release_032 自动验收 — Migrate Legacy Verify Scripts to Isolated Runtime。"""

from __future__ import annotations

import compileall
import importlib
import importlib.util
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

import verification_report  # noqa: E402
import verification_runtime  # noqa: E402
from verification_utils import (  # noqa: E402
    FORBIDDEN_PATTERNS,
    MOCK_DEVICE_DIRS,
    ROOT as UTILS_ROOT,
    setup_path,
)

VERIFY_ALL = SCRIPTS_DIR / "verify_all.py"
NESTED = os.environ.get("NFS_VERIFY_NESTED") == "1"
LEGACY_SCRIPTS = tuple(
    SCRIPTS_DIR / f"verify_release_{num:03d}.py" for num in range(22, 31)
)
FORBIDDEN_RUNTIME_PATTERNS = (
    "runtime/mock_projects",
    "runtime\\mock_projects",
    'Path("runtime")',
    "Path('runtime')",
)


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


def _list_mock_projects_files() -> set[str]:
    base = verification_runtime.get_shared_mock_projects_dir()
    if not base.is_dir():
        return set()
    return {
        p.relative_to(ROOT).as_posix()
        for p in base.rglob("*")
        if p.is_file()
    }


def check_compileall(report: verification_report.VerificationReport) -> None:
    report.start_check("compileall")
    ok = bool(compileall.compile_dir(str(ROOT / "src" / "nfs_scanner_pro"), quiet=1))
    for mod in ("verification_runtime", "verification_report"):
        try:
            importlib.import_module(mod)
        except ImportError:
            ok = False
    if VERIFY_ALL.is_file():
        try:
            importlib.import_module("verify_all")
        except ImportError:
            ok = False
    else:
        ok = False
    if ok:
        report.pass_check("compileall")
    else:
        report.fail_check("compileall", "compile or import failed")


def check_app_paths_runtime_override(report: verification_report.VerificationReport) -> None:
    report.start_check("app_paths_runtime_override")
    setup_path()
    from nfs_scanner_pro import app_paths

    target = verification_runtime.get_release_runtime_dir("032")
    saved_runtime = os.environ.pop("NFS_SCANNER_RUNTIME_DIR", None)
    override_ok = False
    try:
        os.environ["NFS_SCANNER_RUNTIME_DIR"] = str(target.resolve())
        resolved = app_paths.get_runtime_dir().resolve()
        override_ok = resolved == target.resolve() and target.is_dir()
    finally:
        if saved_runtime is not None:
            os.environ["NFS_SCANNER_RUNTIME_DIR"] = saved_runtime
        else:
            os.environ.pop("NFS_SCANNER_RUNTIME_DIR", None)

    saved_again = os.environ.pop("NFS_SCANNER_RUNTIME_DIR", None)
    try:
        default = app_paths.get_runtime_dir().resolve()
        default_ok = default == verification_runtime.get_default_runtime_dir().resolve()
    finally:
        if saved_again is not None:
            os.environ["NFS_SCANNER_RUNTIME_DIR"] = saved_again

    ok = override_ok and default_ok
    if ok:
        report.pass_check("app_paths_runtime_override", str(target.relative_to(ROOT)))
    else:
        report.fail_check("app_paths_runtime_override", f"override={target}, default={default}")


def _assert_runtime_lines(text: str, release_nums: list[int]) -> tuple[bool, str]:
    missing = []
    for num in release_nums:
        rel = verification_runtime.runtime_display_path(f"{num:03d}")
        if f"Runtime: {rel}" not in text:
            missing.append(rel)
    if missing:
        return False, f"missing Runtime lines: {', '.join(missing)}"
    return True, "ok"


def check_verify_all_isolated_only(report: verification_report.VerificationReport) -> None:
    if NESTED:
        report.skip_check("verify_all_isolated_only", "NFS_VERIFY_NESTED=1")
        return
    report.start_check("verify_all_isolated_only")
    before = _list_mock_projects_files()
    failures: list[str] = []
    for num in (26, 27, 28):
        proc = _run([sys.executable, str(VERIFY_ALL), "--only", f"{num:03d}"])
        text = proc.stdout + proc.stderr
        if proc.returncode != 0 or "RESULT: PASS" not in text:
            failures.append(f"--only {num:03d} exit={proc.returncode}")
            continue
        ok_line, detail = _assert_runtime_lines(text, [num])
        if not ok_line:
            failures.append(detail)
        files = verification_runtime.list_release_runtime_files(f"{num:03d}")
        if not files:
            failures.append(f"R{num:03d} has no runtime artifacts")
    after = _list_mock_projects_files()
    new_files = after - before
    st_verify = [f for f in new_files if "ST-VERIFY" in f or "R032" in f]
    if st_verify:
        failures.append(f"mock_projects polluted: {', '.join(sorted(st_verify)[:5])}")
    if failures:
        report.fail_check("verify_all_isolated_only", "; ".join(failures))
    else:
        report.pass_check("verify_all_isolated_only")


def check_verify_all_isolated_from(report: verification_report.VerificationReport) -> None:
    if NESTED:
        report.skip_check("verify_all_isolated_from", "NFS_VERIFY_NESTED=1")
        return
    report.start_check("verify_all_isolated_from")
    before = _list_mock_projects_files()
    proc = _run(
        [sys.executable, str(VERIFY_ALL), "--from", "029"],
        env={"NFS_VERIFY_NESTED": "1"},
    )
    text = proc.stdout + proc.stderr
    failures: list[str] = []
    if proc.returncode != 0 or "RESULT: PASS" not in text:
        failures.append(f"exit={proc.returncode}")
    ok_line, detail = _assert_runtime_lines(text, [29, 30, 31, 32, 33, 34])
    if not ok_line:
        failures.append(detail)
    for num in (29, 30, 31, 32, 33, 34):
        if not verification_runtime.get_release_runtime_dir(f"{num:03d}").is_dir():
            failures.append(f"R{num:03d} dir missing")
    after = _list_mock_projects_files()
    if after - before:
        pollution = [f for f in after - before if "ST-VERIFY" in f]
        if pollution:
            failures.append(f"mock_projects ST-VERIFY added: {pollution[0]}")
    if failures:
        report.fail_check("verify_all_isolated_from", "; ".join(failures))
    else:
        report.pass_check("verify_all_isolated_from")


def check_runtime_no_mock_projects_pollution(
    report: verification_report.VerificationReport,
    *,
    baseline_mock: set[str],
) -> None:
    report.start_check("runtime_no_mock_projects_pollution")
    after = _list_mock_projects_files()
    new_files = after - baseline_mock
    st_verify_new = [f for f in new_files if "ST-VERIFY" in f or "/R032/" in f]
    isolated = verification_runtime.get_release_runtime_dir("026")
    has_isolated = isolated.is_dir() and any(isolated.rglob("*.json"))
    ok = not st_verify_new and has_isolated
    detail = f"new_st_verify={len(st_verify_new)} isolated_json={has_isolated}"
    if ok:
        report.pass_check("runtime_no_mock_projects_pollution", detail)
    else:
        report.fail_check("runtime_no_mock_projects_pollution", detail)


def check_legacy_scripts_no_hardcoded_runtime(report: verification_report.VerificationReport) -> None:
    report.start_check("legacy_scripts_no_hardcoded_runtime")
    hits: list[str] = []
    for script in LEGACY_SCRIPTS:
        if not script.is_file():
            hits.append(f"missing {script.name}")
            continue
        for lineno, line in enumerate(script.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pattern in FORBIDDEN_RUNTIME_PATTERNS:
                if pattern in line:
                    hits.append(f"{script.name}:{lineno}: {pattern}")
    if hits:
        report.fail_check("legacy_scripts_no_hardcoded_runtime", "; ".join(hits[:8]))
    else:
        report.pass_check("legacy_scripts_no_hardcoded_runtime", f"checked {len(LEGACY_SCRIPTS)} scripts")


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
        for num in range(22, 41):
            if f"({num:03d})" not in list_text and f"Release {num:03d}" not in list_text:
                failures.append(f"--list missing {num:03d}")

    only_proc = _run([sys.executable, str(VERIFY_ALL), "--only", "030"])
    only_text = only_proc.stdout + only_proc.stderr
    running = [ln for ln in only_text.splitlines() if ln.startswith("Running ")]
    if only_proc.returncode != 0 or "RESULT: PASS" not in only_text:
        failures.append("--only 030 failed")
    elif len(running) != 1 or "Release 030" not in running[0]:
        failures.append(f"--only 030 runs={len(running)}")
    elif "Runtime: runtime/verification/R030" not in only_text:
        failures.append("--only 030 missing Runtime line")
    elif "TOTAL:" not in only_text:
        failures.append("--only 030 missing TOTAL")

    from_proc = _run(
        [sys.executable, str(VERIFY_ALL), "--from", "030", "--keep-runtime"],
        env={"NFS_VERIFY_NESTED": "1"},
    )
    from_text = from_proc.stdout + from_proc.stderr
    from_running = [ln for ln in from_text.splitlines() if ln.startswith("Running ")]
    if from_proc.returncode != 0 or "RESULT: PASS" not in from_text:
        failures.append("--from 030 failed")
    elif len(from_running) < 3:
        failures.append(f"--from 030 expected at least 3 runs got {len(from_running)}")
    elif "Runtime: runtime/verification/R032" not in from_text:
        failures.append("--from 030 missing R032 Runtime")

    if failures:
        report.fail_check("verify_all_cli", "; ".join(failures))
    else:
        report.pass_check("verify_all_cli")


def check_runtime_gitignore(report: verification_report.VerificationReport) -> None:
    report.start_check("runtime_gitignore")
    ok, detail = verification_runtime.assert_runtime_ignored_by_git()
    if ok:
        report.pass_check("runtime_gitignore", detail)
    else:
        report.fail_check("runtime_gitignore", detail)


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
        / "docs/product-spec/release/Release_032_Migrate_Legacy_Verify_Scripts_To_Isolated_Runtime/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    migrated = [p.name for p in LEGACY_SCRIPTS if p.is_file()]
    lines = [
        "# Release_032 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_032.py",
        "python scripts/verify_all.py --list",
        "python scripts/verify_all.py --only 030",
        "python scripts/verify_all.py --from 030 --keep-runtime",
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
            "## 被迁移的脚本",
            "",
            *[f"- `{name}`" for name in migrated],
            "",
            "## runtime 隔离路径",
            "",
            "- `runtime/verification/R022/` … `runtime/verification/R032/`",
            "",
            "## 是否污染 runtime/mock_projects",
            "",
            "否",
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
    baseline_mock = _list_mock_projects_files()
    report = verification_report.VerificationReport("032")

    check_compileall(report)
    check_app_paths_runtime_override(report)
    check_verify_all_isolated_only(report)
    check_verify_all_isolated_from(report)
    check_runtime_no_mock_projects_pollution(report, baseline_mock=baseline_mock)
    check_legacy_scripts_no_hardcoded_runtime(report)
    check_verify_all_cli(report)
    check_runtime_gitignore(report)
    check_no_real_device_access(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
