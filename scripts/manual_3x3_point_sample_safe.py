#!/usr/bin/env python3
"""3x3 逐点手动确认采样 — 不自动运动、不自动扫描。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.devices.real.hardware_config import is_real_hardware_enabled  # noqa: E402
from nfs_scanner_pro.scan.manual_scan_result_persistence import (  # noqa: E402
    append_manual_sample,
    load_manual_scan_session,
    save_manual_scan_session,
    save_manual_summary,
)
from nfs_scanner_pro.scan.manual_scan_session import (  # noqa: E402
    create_manual_scan_session,
    get_next_pending_point,
    update_point_sample,
    validate_position_near_plan_point,
)
from nfs_scanner_pro.scan.real_scan_plan_persistence import load_scan_plan  # noqa: E402


def _print_default_help() -> None:
    print("未启用真实设备。")
    print("本脚本用于逐点手动确认采样。")
    print("默认不会连接设备、不会移动、不会采样。")
    print("")
    print("用法示例：")
    print("  python scripts/manual_3x3_point_sample_safe.py --create-session --plan <scan_plan.json>")
    print("  python scripts/manual_3x3_point_sample_safe.py --session <manual_scan_session.json> --status")
    print("  python scripts/manual_3x3_point_sample_safe.py --session <path> --point-index 0 --fake-sample")
    print("")
    print("真实采样需同时设置 NFS_ENABLE_REAL_HARDWARE=1 与 --confirm-sample。")


def _load_plan_from_json(plan_path: Path):
    result = load_scan_plan(plan_path)
    if not result.get("ok"):
        raise RuntimeError(result.get("error", "无法加载 scan_plan.json"))
    return result["plan"]


def cmd_create_session(plan_path: Path) -> int:
    plan = _load_plan_from_json(plan_path)
    session = create_manual_scan_session(plan)
    paths = save_manual_scan_session(session)
    print(f"Session ID: {session.session_id}")
    print(f"Plan ID: {session.plan_id}")
    print(f"Point count: {session.point_count()}")
    print(f"Session JSON: {paths['session_json']}")
    print(f"Points CSV: {paths['points_csv']}")
    print(f"Summary JSON: {paths['summary_json']}")
    print("")
    print("Dry run only. No motion command executed.")
    print("No real device connected.")
    return 0


def cmd_status(session_path: Path) -> int:
    session = load_manual_scan_session(session_path)
    next_point = get_next_pending_point(session)
    print(f"Session ID: {session.session_id}")
    print(f"Plan ID: {session.plan_id}")
    print(f"Point count: {session.point_count()}")
    print(f"Sampled: {session.sampled_count()}")
    print(f"Pending: {session.pending_count()}")
    print(f"Failed: {session.failed_count()}")
    print(f"Tolerance: {session.position_tolerance_mm} mm")
    if next_point is not None:
        print(
            f"Next pending: index={next_point.index} "
            f"({next_point.planned_x}, {next_point.planned_y}, {next_point.planned_z})"
        )
    else:
        print("Next pending: —")
    print("")
    for point in session.points:
        print(
            f"  [{point.index}] row={point.row} col={point.col} "
            f"status={point.status} "
            f"planned=({point.planned_x}, {point.planned_y}, {point.planned_z})"
        )
    return 0


def _build_fake_sample_record(session, point_index: int) -> tuple[dict, dict]:
    target = next(p for p in session.points if p.index == point_index)
    sample_id = f"SP-{uuid4().hex[:8].upper()}"
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    validation = validate_position_near_plan_point(
        {"x": target.planned_x, "y": target.planned_y, "z": target.planned_z},
        {"x": target.planned_x, "y": target.planned_y, "z": target.planned_z},
        session.position_tolerance_mm,
    )
    record = {
        "sample_id": sample_id,
        "timestamp_iso": timestamp,
        "project_name": session.project_name,
        "task_id": "MANUAL-3X3-POINT",
        "position": {
            "x": target.planned_x,
            "y": target.planned_y,
            "z": target.planned_z,
            "source": "fake",
            "state": "Idle",
        },
        "spectrum": {
            "frequency_hz": 2450000000.0,
            "frequency_ghz": 2.45,
            "amplitude_dbm": -23.45,
            "unit": "dBm",
            "source": "fake",
            "raw": "-23.45",
        },
        "safe_mode": True,
        "real_hardware": False,
        "motion_command_executed": False,
        "sweep_started": False,
    }
    return record, validation


def cmd_fake_sample(session_path: Path, point_index: int) -> int:
    session = load_manual_scan_session(session_path)
    record, validation = _build_fake_sample_record(session, point_index)
    update_result = update_point_sample(session, point_index, record, validation)
    if not update_result.get("ok"):
        print(f"更新失败：{update_result.get('error', '')}")
        return 1
    target = next(p for p in session.points if p.index == point_index)
    paths = save_manual_scan_session(session)
    samples_path = append_manual_sample(session, target, record)
    save_manual_summary(session)
    print(f"Fake sample point {point_index}: PASS")
    print(f"Sample ID: {record['sample_id']}")
    print(f"Sampled count: {session.sampled_count()}")
    print(f"Pending count: {session.pending_count()}")
    print(f"Session JSON: {paths['session_json']}")
    print(f"Samples CSV: {samples_path}")
    print("No real device connected. No motion. No sweep.")
    return 0


def cmd_real_sample(session_path: Path, point_index: int) -> int:
    if not is_real_hardware_enabled():
        print("拒绝：未设置 NFS_ENABLE_REAL_HARDWARE=1")
        return 1

    from nfs_scanner_pro.devices.real import RealDeviceManager

    session = load_manual_scan_session(session_path)
    target = next((p for p in session.points if p.index == point_index), None)
    if target is None:
        print(f"点 index={point_index} 不存在")
        return 1

    manager = RealDeviceManager()
    try:
        result = manager.manual_sample_plan_point_safe(
            {
                "index": target.index,
                "x": target.planned_x,
                "y": target.planned_y,
                "z": target.planned_z,
            },
            session.position_tolerance_mm,
            save=False,
        )
        if result.get("disabled"):
            print(f"采样禁用：{result.get('error', '')}")
            return 1

        validation = result.get("position_validation", {})
        record = result.get("record")
        if record is None:
            validation = validation or {"ok": False, "reason": result.get("error", "采样失败")}
            update_point_sample(session, point_index, {}, validation)
            save_manual_scan_session(session)
            save_manual_summary(session)
            print(f"采样失败：{result.get('error', validation.get('reason', ''))}")
            return 1

        update_point_sample(session, point_index, record, validation)
        if validation.get("ok"):
            updated = next(p for p in session.points if p.index == point_index)
            paths = save_manual_scan_session(session)
            samples_path = append_manual_sample(session, updated, record)
            save_manual_summary(session)
            print(f"Real sample point {point_index}: PASS")
            print(f"Sample ID: {record.get('sample_id', '')}")
            print(f"Position error: {validation.get('error_mm')} mm")
            print(f"Amplitude: {record.get('spectrum', {}).get('amplitude_dbm')} dBm")
            print(f"Session JSON: {paths['session_json']}")
            print(f"Samples CSV: {samples_path}")
            print("Motion command executed: false")
            print("Sweep started: false")
            return 0

        update_point_sample(session, point_index, record, validation)
        save_manual_scan_session(session)
        save_manual_summary(session)
        print(f"位置校验失败：{validation.get('reason', '')}")
        return 1
    finally:
        manager.disconnect_all()
        print("Disconnect done")


def main() -> int:
    parser = argparse.ArgumentParser(description="3x3 逐点手动确认采样")
    parser.add_argument("--create-session", action="store_true")
    parser.add_argument("--plan", type=Path, help="scan_plan.json 路径")
    parser.add_argument("--session", type=Path, help="manual_scan_session.json 路径")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--point-index", type=int)
    parser.add_argument("--confirm-sample", action="store_true")
    parser.add_argument("--fake-sample", action="store_true")
    args = parser.parse_args()

    if args.create_session:
        if args.plan is None:
            print("需要 --plan <scan_plan.json>")
            return 1
        return cmd_create_session(args.plan)

    if args.session is not None and args.status:
        return cmd_status(args.session)

    if args.session is not None and args.point_index is not None:
        if args.fake_sample:
            return cmd_fake_sample(args.session, args.point_index)
        if args.confirm_sample:
            return cmd_real_sample(args.session, args.point_index)
        print("拒绝采样：缺少 --confirm-sample 或 --fake-sample。")
        print("逐点手动采样必须显式确认，不会自动连接设备或采样。")
        return 0

    _print_default_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
