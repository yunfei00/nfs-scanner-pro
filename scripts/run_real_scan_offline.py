#!/usr/bin/env python3
"""真实扫描 offline 执行 — dry-run / fake-run / real-run（默认 dry-run）。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.scan.real_scan_executor import RealScanExecutor  # noqa: E402
from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan  # noqa: E402
from nfs_scanner_pro.scan.real_scan_plan_persistence import load_scan_plan  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="真实扫描 offline 执行器")
    parser.add_argument("--plan", type=Path, help="scan_plan.json 路径")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--fake-run", action="store_true")
    parser.add_argument("--real-run", action="store_true")
    args = parser.parse_args()

    if args.fake_run:
        mode = "fake_run"
    elif args.real_run:
        mode = "real_run"
    else:
        mode = "dry_run"

    if args.plan:
        loaded = load_scan_plan(args.plan)
        if not loaded.get("ok"):
            print(f"加载计划失败：{loaded.get('error', '')}")
            return 1
        plan = loaded["plan"]
    else:
        plan = generate_3x3_scan_plan()

    executor = RealScanExecutor()
    load_result = executor.load_plan(plan)
    print(f"Task ID: {load_result.get('task_id', '')}")
    print(f"Mode: {mode}")

    if mode == "dry_run":
        result = executor.dry_run()
    elif mode == "fake_run":
        result = executor.fake_run()
    else:
        print("警告：real-run 需要多项 NFS_ENABLE_REAL_* 安全开关，默认 blocked。")
        result = executor.real_run()

    print(f"Result: ok={result.get('ok')} blocked={result.get('blocked', False)}")
    paths = result.get("paths", {})
    for key, path in paths.items():
        print(f"{key}: {path}")
    return 0 if result.get("ok") or result.get("blocked") else 1


if __name__ == "__main__":
    raise SystemExit(main())
