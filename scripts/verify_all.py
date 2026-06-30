#!/usr/bin/env python3
"""统一验收入口 — 运行所有 verify_release_xxx.py（Release_031 增强）。"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

VERIFY_SCRIPTS: tuple[tuple[int, str, Path], ...] = (
    (22, "Release 022", SCRIPTS / "verify_release_022.py"),
    (23, "Release 023", SCRIPTS / "verify_release_023.py"),
    (24, "Release 024", SCRIPTS / "verify_release_024.py"),
    (25, "Release 025", SCRIPTS / "verify_release_025.py"),
    (26, "Release 026", SCRIPTS / "verify_release_026.py"),
    (27, "Release 027", SCRIPTS / "verify_release_027.py"),
    (28, "Release 028", SCRIPTS / "verify_release_028.py"),
    (29, "Release 029", SCRIPTS / "verify_release_029.py"),
    (30, "Release 030", SCRIPTS / "verify_release_030.py"),
    (31, "Release 031", SCRIPTS / "verify_release_031.py"),
)

TAIL_LINES = 80


@dataclass
class RunOutcome:
    label: str
    number: int
    status: str
    elapsed_s: float
    exit_code: int
    stdout: str
    stderr: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run NFS Scanner verification scripts.")
    parser.add_argument(
        "--only",
        type=int,
        metavar="NNN",
        help="Run only verify_release_NNN.py (e.g. 026)",
    )
    parser.add_argument(
        "--from",
        dest="from_release",
        type=int,
        metavar="NNN",
        help="Run from verify_release_NNN.py through the latest",
    )
    parser.add_argument(
        "--no-fail-fast",
        action="store_true",
        help="Continue running after a failure (default: stop on first FAIL)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List registered scripts and exit",
    )
    return parser.parse_args(argv)


def select_scripts(args: argparse.Namespace) -> list[tuple[int, str, Path]]:
    if args.only is not None:
        selected = [item for item in VERIFY_SCRIPTS if item[0] == args.only]
        if not selected:
            raise SystemExit(f"No script registered for Release {args.only:03d}")
        return selected
    if args.from_release is not None:
        return [item for item in VERIFY_SCRIPTS if item[0] >= args.from_release]
    return list(VERIFY_SCRIPTS)


def list_scripts() -> None:
    print("Registered verification scripts:\n")
    for number, label, path in VERIFY_SCRIPTS:
        exists = "ok" if path.is_file() else "MISSING"
        print(f"  {label} ({number:03d})  {path.name}  [{exists}]")
    print(f"\nTotal: {len(VERIFY_SCRIPTS)}")


def parse_result(stdout: str, exit_code: int) -> str:
    result_line = "FAIL"
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped == "RESULT: PASS":
            result_line = "PASS"
        elif stripped == "RESULT: FAIL":
            result_line = "FAIL"
    if exit_code == 0 and result_line != "FAIL":
        return "PASS"
    if exit_code != 0:
        return "FAIL"
    return result_line


def tail_output(text: str, lines: int = TAIL_LINES) -> str:
    parts = text.splitlines()
    if len(parts) <= lines:
        return text
    return "\n".join(parts[-lines:])


def run_script(number: int, label: str, path: Path) -> RunOutcome:
    if not path.is_file():
        return RunOutcome(
            label=label,
            number=number,
            status="SKIPPED",
            elapsed_s=0.0,
            exit_code=0,
            stdout="",
            stderr=f"missing {path}",
        )

    print(f"Running {label} ...", flush=True)
    started = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed = time.perf_counter() - started
    status = parse_result(proc.stdout, proc.returncode)
    return RunOutcome(
        label=label,
        number=number,
        status=status,
        elapsed_s=elapsed,
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def print_failure_tail(outcome: RunOutcome) -> None:
    print(f"\n--- Failure tail: {outcome.label} (exit {outcome.exit_code}) ---")
    if outcome.stdout.strip():
        print(tail_output(outcome.stdout))
    if outcome.stderr.strip():
        print("--- stderr ---", file=sys.stderr)
        print(tail_output(outcome.stderr), file=sys.stderr)
    print("--- end failure tail ---\n")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.list:
        list_scripts()
        return 0

    scripts = select_scripts(args)
    fail_fast = not args.no_fail_fast

    print("Verification Suite\n")
    suite_started = time.perf_counter()
    outcomes: list[RunOutcome] = []
    exit_code = 0

    for number, label, path in scripts:
        outcome = run_script(number, label, path)
        outcomes.append(outcome)
        print(f"{label}: {outcome.status}  {outcome.elapsed_s:.2f}s")
        if outcome.status == "FAIL" or (outcome.status != "SKIPPED" and outcome.exit_code != 0):
            exit_code = 1
            print_failure_tail(outcome)
            if fail_fast:
                break

    total = time.perf_counter() - suite_started
    print()
    for outcome in outcomes:
        print(f"{outcome.label}: {outcome.status}  {outcome.elapsed_s:.2f}s")
    print(f"\nTOTAL: {total:.2f}s")
    if exit_code == 0:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
