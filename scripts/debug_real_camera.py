#!/usr/bin/env python3
"""相机调试 CLI — 默认不打开真实相机。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.devices.real import CameraAdapter, load_hardware_config  # noqa: E402
from nfs_scanner_pro.devices.real.transports import FakeCameraTransport  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="真实相机调试（默认 dry-run）")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--fake", action="store_true")
    args = parser.parse_args()

    config = load_hardware_config()
    camera = CameraAdapter(config.camera)
    if args.fake:
        camera.bind_transport(FakeCameraTransport())
        camera.connect()
        print("Mode: fake camera")
    else:
        print("Mode: dry-run / disabled（默认不打开真实相机）")

    if args.list or not args.capture:
        print(f"Devices: {camera.enumerate_devices()}")
        return 0

    if args.fake:
        print(camera.capture_image(dry_run=False))
    else:
        print(camera.capture_image(dry_run=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
