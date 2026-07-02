#!/usr/bin/env python3
"""3x3 小区域扫描 dry-run 计划生成 — 不连接设备、不运动、不采样。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan  # noqa: E402
from nfs_scanner_pro.scan.real_scan_plan_persistence import save_scan_plan  # noqa: E402
from nfs_scanner_pro.scan.real_scan_safety import (  # noqa: E402
    ScanSafetyLimits,
    mark_plan_points_safe,
    validate_scan_plan,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="生成 3x3 小区域扫描 dry-run 计划（不运动 / 不采样）"
    )
    parser.add_argument("--center-x", type=float, default=50.0)
    parser.add_argument("--center-y", type=float, default=-50.0)
    parser.add_argument("--z", type=float, default=5.0)
    parser.add_argument("--step", type=float, default=0.5, help="点间距 mm")
    parser.add_argument("--project", default="Manual_Check")
    parser.add_argument("--region", default="SmallArea_3x3")
    parser.add_argument("--frequency", default="2.450 GHz")
    parser.add_argument("--trace", default="Trace 1")
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="只打印计划，不保存文件",
    )
    args = parser.parse_args()

    limits = ScanSafetyLimits.from_env()
    if args.step > limits.max_step_mm:
        print(
            f"拒绝：步长 {args.step} mm 超过上限 NFS_SCAN_MAX_STEP_MM={limits.max_step_mm}"
        )
        return 1

    plan = generate_3x3_scan_plan(
        project_name=args.project,
        region_name=args.region,
        center_x=args.center_x,
        center_y=args.center_y,
        z=args.z,
        step_mm=args.step,
        frequency=args.frequency,
        trace=args.trace,
    )
    validation = validate_scan_plan(plan, limits=limits)
    mark_plan_points_safe(plan, validation)

    print(f"Plan ID: {plan.plan_id}")
    print(f"Project: {plan.project_name}")
    print(f"Region: {plan.region_name}")
    print(f"Center: X={args.center_x} Y={args.center_y} Z={args.z}")
    print(f"Step: {args.step} mm")
    print(f"Points: {plan.point_count()} (3x3 serpentine)")
    print("")
    print("Planned points:")
    for point in plan.points:
        print(
            f"  [{point.index}] row={point.row} col={point.col} "
            f"X={point.x:.3f} Y={point.y:.3f} Z={point.z:.3f} "
            f"safe={point.safe_checked}"
        )
    print("")

    if not validation.get("ok"):
        print(f"Safety validation: FAIL — {validation.get('summary', '')}")
        for item in validation.get("failed_points", []):
            print(f"  point {item.get('index')}: {item.get('reason', '')}")
        return 1

    print(f"Safety validation: PASS — {validation.get('summary', '')}")
    print("")
    print("Dry run only.")
    print("No motion command executed.")
    print("No spectrum sweep started.")
    print("No real device connected.")

    if args.no_save:
        return 0

    paths = save_scan_plan(plan, validation)
    print("")
    print(f"Saved scan_plan.json: {paths['json_path']}")
    print(f"Saved scan_plan.csv: {paths['csv_path']}")
    print(f"Saved scan_plan_summary.json: {paths['summary_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
