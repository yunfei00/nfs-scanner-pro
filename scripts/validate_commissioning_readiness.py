#!/usr/bin/env python3
"""联调准备条件验证 — Release 048。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.hardware_commissioning.commissioning_workflow import (
    build_default_workflow,
    validate_workflow,
)

RELEASE_047_DOCS = (
    "docs/hardware/README.md",
    "docs/hardware/hardware-safety-switches.md",
    "docs/hardware/hardware-debug-command-map.md",
)

RELEASE_048_DOCS = (
    "docs/hardware/commissioning/README.md",
    "docs/hardware/commissioning/00-overview.md",
    "docs/hardware/commissioning/10-real-run-gate.md",
)

CONFIG_FILES = (
    "config/hardware.example.yaml",
    "config/commissioning.workflow.example.yaml",
)

CLI_SCRIPTS = (
    "start_hardware_commissioning.py",
    "generate_commissioning_template.py",
    "check_hardware_interface_inventory.py",
    "generate_hardware_bringup_report.py",
)


def main() -> int:
    failed: list[str] = []

    for doc in RELEASE_047_DOCS + RELEASE_048_DOCS:
        if not (ROOT / doc).is_file():
            failed.append(f"missing doc: {doc}")

    for cfg in CONFIG_FILES:
        if not (ROOT / cfg).is_file():
            failed.append(f"missing config: {cfg}")

    for script in CLI_SCRIPTS:
        if not (ROOT / "scripts" / script).is_file():
            failed.append(f"missing script: {script}")

    wf = build_default_workflow()
    validation = validate_workflow(wf)
    if not validation.get("ok"):
        failed.append(f"workflow invalid: {validation.get('missing_stage_ids')}")

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_hardware_interface_inventory.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        failed.append("interface inventory failed")

    safety = (ROOT / "docs/hardware/hardware-safety-switches.md").read_text(encoding="utf-8")
    for key in (
        "NFS_ENABLE_REAL_HARDWARE",
        "NFS_ENABLE_REAL_SCAN_EXECUTION",
        "NFS_ENABLE_REAL_MOTION_JOG",
    ):
        if key not in safety:
            failed.append(f"safety doc missing {key}")

    if failed:
        print("COMMISSIONING READINESS: FAIL")
        for item in failed:
            print(f"  - {item}")
        return 1

    print("COMMISSIONING READINESS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
