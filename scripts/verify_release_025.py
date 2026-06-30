#!/usr/bin/env python3
"""Release_025 自动验收 — CI Verification Integration。"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from verification_utils import (  # noqa: E402
    FORBIDDEN_PATTERNS,
    GITIGNORE_REQUIRED,
    MOCK_DEVICE_DIRS,
    ROOT,
    CheckResult,
    check_gitignore,
    check_no_real_device_access,
    setup_offscreen,
    setup_path,
)

WORKFLOW_PATH = ROOT / ".github/workflows/verify.yml"
VERIFY_ALL_PATH = ROOT / "scripts/verify_all.py"

WORKFLOW_REQUIRED_SNIPPETS = (
    "push:",
    "pull_request:",
    "main",
    "windows-latest",
    "setup-python",
    "python -m compileall src/nfs_scanner_pro",
    "python scripts/verify_all.py",
    "QT_QPA_PLATFORM",
)

VERIFY_ALL_REQUIRED = (
    "verify_release_022.py",
    "verify_release_023.py",
    "verify_release_024.py",
    "verify_release_025.py",
)

PREVIOUS_VERIFY_SCRIPTS = (
    SCRIPTS_DIR / "verify_release_022.py",
    SCRIPTS_DIR / "verify_release_023.py",
    SCRIPTS_DIR / "verify_release_024.py",
)


def check_workflow_exists(check: CheckResult) -> None:
    ok = WORKFLOW_PATH.is_file()
    check.add("workflow_exists", ok, str(WORKFLOW_PATH.relative_to(ROOT)) if ok else "missing")


def check_workflow_triggers(check: CheckResult) -> None:
    text = WORKFLOW_PATH.read_text(encoding="utf-8") if WORKFLOW_PATH.is_file() else ""
    ok = all(snippet in text for snippet in ("push:", "pull_request:", "main"))
    check.add("workflow_triggers", ok)


def check_workflow_python(check: CheckResult) -> None:
    text = WORKFLOW_PATH.read_text(encoding="utf-8") if WORKFLOW_PATH.is_file() else ""
    ok = "windows-latest" in text and "setup-python" in text
    check.add("workflow_python", ok)


def check_workflow_commands(check: CheckResult) -> None:
    text = WORKFLOW_PATH.read_text(encoding="utf-8") if WORKFLOW_PATH.is_file() else ""
    ok = all(snippet in text for snippet in WORKFLOW_REQUIRED_SNIPPETS)
    missing = [s for s in WORKFLOW_REQUIRED_SNIPPETS if s not in text]
    check.add("workflow_commands", ok, ", ".join(missing) if missing else "ok")


def check_verify_all_registered(check: CheckResult) -> None:
    text = VERIFY_ALL_PATH.read_text(encoding="utf-8") if VERIFY_ALL_PATH.is_file() else ""
    ok = all(name in text for name in VERIFY_ALL_REQUIRED)
    missing = [name for name in VERIFY_ALL_REQUIRED if name not in text]
    check.add("verify_all_registered", ok, ", ".join(missing) if missing else "ok")


def check_gitignore_runtime(check: CheckResult) -> None:
    check_gitignore(check, name="gitignore_runtime")


def run_previous_release_verifications(check: CheckResult) -> None:
    import verification_runtime

    setup_offscreen()
    failed: list[str] = []
    release_map = {
        "verify_release_022.py": "022",
        "verify_release_023.py": "023",
        "verify_release_024.py": "024",
    }
    for script in PREVIOUS_VERIFY_SCRIPTS:
        if not script.is_file():
            failed.append(f"missing {script.name}")
            continue
        release_id = release_map.get(script.name, "022")
        env = verification_runtime.build_release_env(release_id)
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        if proc.returncode != 0:
            failed.append(f"{script.name} exit={proc.returncode}")
    check.add(
        "previous_release_verifications",
        not failed,
        "; ".join(failed) if failed else "022/023/024 PASS",
    )


def check_no_high_fidelity_changes(check: CheckResult) -> None:
    hits: list[str] = []
    try:
        for cmd in (
            ["git", "diff", "--name-only", "HEAD"],
            ["git", "diff", "--cached", "--name-only"],
        ):
            proc = subprocess.run(
                cmd,
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if proc.returncode != 0:
                continue
            for line in proc.stdout.splitlines():
                lowered = line.replace("\\", "/").lower()
                if "high_fidelity" in lowered or "high-fidelity" in lowered:
                    hits.append(line.strip())
    except OSError as exc:
        check.add("no_high_fidelity_changes", False, str(exc))
        return
    check.add("no_high_fidelity_changes", not hits, "; ".join(hits))


def write_acceptance_report(check: CheckResult) -> Path:
    report_path = (
        ROOT
        / "docs/product-spec/release/Release_025_CI_Verification_Integration/ACCEPTANCE_REPORT.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    verify_all_text = (
        VERIFY_ALL_PATH.read_text(encoding="utf-8") if VERIFY_ALL_PATH.is_file() else ""
    )
    includes_025 = "verify_release_025.py" in verify_all_text
    lines = [
        "# Release_025 验收报告",
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_025.py",
        "python scripts/verify_all.py",
        "```",
        "",
        "## 验收时间",
        "",
        now,
        "",
        "## 检查项",
        "",
    ]
    for name, ok, detail in check.results:
        status = "PASS" if ok else "FAIL"
        suffix = f" — {detail}" if detail else ""
        lines.append(f"- [{status}] `{name}`{suffix}")
    lines.extend(
        [
            "",
            "## 结果",
            "",
            "PASS" if check.passed else "FAIL",
            "",
            "## workflow 路径",
            "",
            "`.github/workflows/verify.yml`",
            "",
            "## verify_release_025.py 路径",
            "",
            "`scripts/verify_release_025.py`",
            "",
            "## verify_all.py 是否包含 Release_025",
            "",
            "是" if includes_025 else "否",
            "",
            "## 是否接真实设备",
            "",
            "否",
            "",
            "## 是否生成真实 PDF / Word / Excel",
            "",
            "否",
            "",
            "## 是否可以提交",
            "",
            "是" if check.passed else "否",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    setup_path()
    check = CheckResult("Release_025 Verification")
    check_workflow_exists(check)
    check_workflow_triggers(check)
    check_workflow_python(check)
    check_workflow_commands(check)
    check_verify_all_registered(check)
    check_gitignore_runtime(check)
    run_previous_release_verifications(check)
    check_no_high_fidelity_changes(check)
    check_no_real_device_access(check)
    report_path = write_acceptance_report(check)
    check.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return 0 if check.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
