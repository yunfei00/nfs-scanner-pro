#!/usr/bin/env python3
"""真实运动平台手动安全点动 — 需双重开关与 --confirm。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.devices.real import (  # noqa: E402
    MotionGrblAdapter,
    RealDeviceManager,
    is_real_hardware_enabled,
    is_real_motion_jog_enabled,
    load_hardware_config,
)


def _format_position(pos: dict) -> str:
    return (
        f"X={pos.get('x', 0):.3f} "
        f"Y={pos.get('y', 0):.3f} "
        f"Z={pos.get('z', 0):.3f}"
    )


def _run_dry_run_preview(
    adapter: MotionGrblAdapter,
    axis: str,
    direction: str,
    step: float,
    *,
    port: str,
) -> int:
    print(f"Motion port: {port}")
    print(f"Axis: {axis.lower()}  Direction: {direction}  Step: {step:.3f} mm")
    print("Dry-run: yes")

    current = {"x": adapter.x, "y": adapter.y, "z": adapter.z}
    validation = adapter.validate_jog(axis, direction, step, current)
    if not validation.get("ok"):
        print(f"点动校验失败：{validation.get('reason', '')}")
        return 1

    command = adapter.build_jog_command(axis, direction, step)
    target = validation.get("target_position", {})
    print(f"Command: {command}")
    print(f"Position before: {_format_position(current)}")
    print(f"Target position: {_format_position(target)}")
    print("Position after:  (dry-run，未移动)")
    print("dry-run：未发送点动命令")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="真实运动平台手动安全点动")
    parser.add_argument("--axis", required=True, help="点动轴：x / y / z")
    parser.add_argument("--direction", required=True, help="方向：+ / -")
    parser.add_argument("--step", type=float, required=True, help="步长 (mm)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅校验并输出命令，不发送真实点动",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="确认执行真实点动（仍需 NFS_ENABLE_REAL_MOTION_JOG=1）",
    )
    args = parser.parse_args()

    if args.step <= 0:
        print(f"拒绝点动：步长 {args.step} mm 必须大于 0")
        return 1

    config = load_hardware_config()
    if args.step > config.motion_safety.max_jog_step_mm:
        print(
            "拒绝点动：步长 "
            f"{args.step:.3f} mm 超过最大允许 "
            f"{config.motion_safety.max_jog_step_mm:.3f} mm"
        )
        return 1

    if not args.confirm and not args.dry_run:
        print("未提供 --confirm，不会执行真实点动。")
        print("如需 dry-run 预览，请添加 --dry-run。")
        print("如需真实点动，请同时设置 NFS_ENABLE_REAL_MOTION_JOG=1 并添加 --confirm。")
        return 0

    if args.dry_run:
        adapter = MotionGrblAdapter(config.motion, config.motion_safety)
        return _run_dry_run_preview(
            adapter,
            args.axis,
            args.direction,
            args.step,
            port=config.motion.port,
        )

    if not is_real_hardware_enabled():
        print("真实硬件未启用。")
        print("请设置：NFS_ENABLE_REAL_HARDWARE=1")
        return 0

    if not is_real_motion_jog_enabled():
        print("真实点动未启用。")
        print("请设置：NFS_ENABLE_REAL_MOTION_JOG=1")
        return 0

    manager = RealDeviceManager(config)
    print(f"Motion port: {config.motion.port}")
    print(f"Axis: {args.axis.lower()}  Direction: {args.direction}  Step: {args.step:.3f} mm")
    print("Dry-run: no")

    exit_code = 0
    try:
        connect_msg = manager.motion.connect()
        print(f"Connect: {connect_msg}")
        if not manager.motion.is_connected():
            print("连接失败，无法点动。")
            return 1

        result = manager.motion_safe_jog(
            args.axis,
            args.direction,
            args.step,
            dry_run=False,
        )

        if result.get("blocked"):
            print(f"点动被阻断：{result.get('message', '')}")
            return 0

        if not result.get("ok"):
            print(f"点动失败：{result.get('error', '未知错误')}")
            if result.get("target_position"):
                print(f"目标位置：{_format_position(result['target_position'])}")
            return 1

        before = result.get("position_before", {})
        target = result.get("target_position", {})
        after = result.get("position_after", {})

        print(f"Command: {result.get('command', '')}")
        print(f"Position before: {_format_position(before)}")
        print(f"Target position: {_format_position(target)}")
        print(f"Position after:  {_format_position(after)}")
        print(result.get("message", "完成"))
    except Exception as exc:  # noqa: BLE001
        print(f"执行失败：{exc}")
        exit_code = 1
    finally:
        if manager.motion.is_connected():
            manager.motion.disconnect()
            print("Disconnect done")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
