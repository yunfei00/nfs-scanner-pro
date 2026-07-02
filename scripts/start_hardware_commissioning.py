#!/usr/bin/env python3
"""硬件现场联调向导 — Release 048。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.hardware_commissioning.commissioning_persistence import save_session
from nfs_scanner_pro.hardware_commissioning.commissioning_runner import CommissioningRunner
from nfs_scanner_pro.hardware_commissioning.commissioning_workflow import load_commissioning_workflow

NEXT_STEPS = [
    "1. 复制 config/commissioning.local.example.yaml → commissioning.local.yaml",
    "2. 运行 validate_commissioning_readiness.py 确认准备就绪",
    "3. offline → fake → real-safe 顺序执行",
    "4. 现场步骤需 manual confirm 后 mark",
    "5. real-run 仅在 gate 全部满足且后续 Release 启用",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="硬件现场联调向导")
    parser.add_argument("--mode", choices=("offline", "fake", "real-safe"), default="offline")
    parser.add_argument("--workflow", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--stage", default=None)
    parser.add_argument("--step", default=None)
    parser.add_argument("--show-gates", action="store_true")
    parser.add_argument("--no-save", action="store_true")
    args = parser.parse_args()

    workflow = load_commissioning_workflow(args.workflow)
    runner = CommissioningRunner(workflow_path=args.workflow)
    runner.session.mode = args.mode

    if args.stage:
        runner.run_stage(args.stage)
    elif args.step:
        runner.run_step(args.step)
    elif args.mode == "offline":
        runner.run_offline()
    elif args.mode == "fake":
        runner.run_fake()
    else:
        runner.run_real_safe()

    session = runner.session
    paths = {}
    if not args.no_save:
        base = Path(args.output) if args.output else None
        paths = save_session(session, base=base)

    print(f"session_id: {session.session_id}")
    print(f"mode: {session.mode}")
    print(f"total_steps: {session.total_steps()}")
    print(f"passed_steps: {session.passed_steps()}")
    print(f"failed_steps: {session.failed_steps()}")
    print(f"blocked_steps: {session.blocked_steps()}")
    print(f"ready_for_real_run: {session.is_ready_for_real_run()}")
    if paths:
        print(f"report: {paths.get('report_md', '')}")
    if args.show_gates:
        print(f"gate: {session.gate.as_dict()}")
    print("")
    print("Next manual steps:")
    for line in NEXT_STEPS:
        print(f"  {line}")
    return 0 if session.failed_steps() == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
