#!/usr/bin/env python3
"""统一验收入口 — 运行所有 verify_release_xxx.py。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

VERIFY_SCRIPTS = (
    ("Release 022", SCRIPTS / "verify_release_022.py"),
    ("Release 023", SCRIPTS / "verify_release_023.py"),
    ("Release 024", SCRIPTS / "verify_release_024.py"),
    ("Release 025", SCRIPTS / "verify_release_025.py"),
    ("Release 026", SCRIPTS / "verify_release_026.py"),
    ("Release 027", SCRIPTS / "verify_release_027.py"),
    ("Release 028", SCRIPTS / "verify_release_028.py"),
    ("Release 029", SCRIPTS / "verify_release_029.py"),
    ("Release 030", SCRIPTS / "verify_release_030.py"),
)


def run_script(label: str, path: Path) -> tuple[str, int]:
    if not path.is_file():
        print(f"{label}: SKIPPED (missing {path.name})")
        return "SKIPPED", 0
    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    result_line = "FAIL"
    for line in proc.stdout.splitlines():
        if line.strip() == "RESULT: PASS":
            result_line = "PASS"
        elif line.strip() == "RESULT: FAIL":
            result_line = "FAIL"
    if proc.returncode != 0 and result_line != "PASS":
        result_line = "FAIL"
    elif proc.returncode == 0:
        result_line = "PASS"
    print(f"{label}: {result_line}")
    if result_line == "FAIL":
        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
    return result_line, proc.returncode


def main() -> int:
    print("Verification Suite\n")
    outcomes: list[str] = []
    exit_code = 0
    for label, script in VERIFY_SCRIPTS:
        outcome, code = run_script(label, script)
        outcomes.append(outcome)
        if outcome == "FAIL" or (outcome != "SKIPPED" and code != 0):
            exit_code = 1
    print()
    if exit_code == 0:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
