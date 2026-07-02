#!/usr/bin/env python3
"""舵机调试 CLI — 默认不控制真实舵机。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.devices.real import ServoAdapter, load_hardware_config  # noqa: E402
from nfs_scanner_pro.devices.real.transports import FakeServoTransport  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="真实舵机调试（默认 dry-run）")
    parser.add_argument("--state", action="store_true")
    parser.add_argument("--hx", action="store_true")
    parser.add_argument("--hy", action="store_true")
    parser.add_argument("--calibrate", action="store_true")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--fake", action="store_true")
    args = parser.parse_args()

    config = load_hardware_config()
    servo = ServoAdapter(config.servo)
    if args.fake:
        servo.bind_transport(FakeServoTransport())
        servo.connect()
        print("Mode: fake servo")
    else:
        print("Mode: dry-run / disabled（默认不控制真实舵机）")

    if args.state or not any([args.hx, args.hy, args.calibrate]):
        print(servo.get_state() if args.fake else servo.snapshot())
        return 0

    dry = args.dry_run and not args.fake
    if args.hx:
        print(servo.switch_hx(dry_run=dry))
    if args.hy:
        print(servo.switch_hy(dry_run=dry))
    if args.calibrate:
        print(servo.calibrate(dry_run=dry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
