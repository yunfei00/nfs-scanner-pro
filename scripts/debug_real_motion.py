#!/usr/bin/env python3
"""运动平台调试 CLI — 默认 dry-run，不连接真实设备。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.devices.real import MotionGrblAdapter, load_hardware_config  # noqa: E402
from nfs_scanner_pro.devices.real.transports import FakeSerialTransport  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="真实运动平台调试（默认 dry-run）")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--jog", nargs=3, metavar=("AXIS", "DIR", "STEP"))
    parser.add_argument("--move-to", action="store_true")
    parser.add_argument("--x", type=float)
    parser.add_argument("--y", type=float)
    parser.add_argument("--z", type=float)
    parser.add_argument("--home", action="store_true")
    parser.add_argument("--estop", action="store_true")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--fake", action="store_true")
    args = parser.parse_args()

    config = load_hardware_config()
    motion = MotionGrblAdapter(config.motion, config.motion_safety)
    if args.fake:
        motion.bind_transport(FakeSerialTransport())
        motion.connect()
        print("Mode: fake transport")
    else:
        print("Mode: dry-run / disabled（未设置 NFS_ENABLE_REAL_HARDWARE=1 时不连接真实设备）")

    if args.status or not any([args.jog, args.move_to, args.home, args.estop]):
        if args.fake:
            status = motion.query_status()
            print(f"Status: {status}")
        else:
            snap = motion.snapshot()
            print(f"Snapshot: enabled={snap.get('enabled')} connected={snap.get('connected')}")
        return 0

    dry = args.dry_run and not args.fake
    if args.jog:
        axis, direction, step = args.jog
        result = motion.safe_jog(axis, direction, float(step), dry_run=dry)
        print(result)
    if args.move_to:
        result = motion.move_to(args.x, args.y, args.z, dry_run=dry)
        print(result)
    if args.home:
        print(motion.home(dry_run=dry))
    if args.estop:
        print(motion.emergency_stop(dry_run=dry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
