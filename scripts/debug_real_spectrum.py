#!/usr/bin/env python3
"""频谱仪调试 CLI — 默认 dry-run / fake。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.devices.real import SpectrumScpiAdapter, load_hardware_config  # noqa: E402
from nfs_scanner_pro.devices.real.transports import FakeScpiTransport  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="真实频谱仪调试（默认 dry-run）")
    parser.add_argument("--idn", action="store_true")
    parser.add_argument("--marker", action="store_true")
    parser.add_argument("--trace-info", action="store_true")
    parser.add_argument("--trace-data", action="store_true")
    parser.add_argument("--configure", action="store_true")
    parser.add_argument("--sweep", action="store_true")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--fake", action="store_true")
    args = parser.parse_args()

    config = load_hardware_config()
    spectrum = SpectrumScpiAdapter(config.spectrum)
    if args.fake:
        spectrum.bind_transport(FakeScpiTransport())
        spectrum.connect()
        print("Mode: fake transport")
    else:
        print("Mode: dry-run / disabled（默认不连接真实频谱仪）")

    if args.idn or not any(
        [args.marker, args.trace_info, args.trace_data, args.configure, args.sweep]
    ):
        if args.fake:
            print(spectrum.query_idn())
        else:
            print(spectrum.snapshot())
        return 0

    dry = args.dry_run and not args.fake
    if args.marker:
        print(spectrum.read_marker_amplitude() if args.fake else {"dry_run": True})
    if args.trace_info:
        print(spectrum.read_trace_info() if args.fake else {"dry_run": True})
    if args.trace_data:
        print(spectrum.read_trace_data() if args.fake else {"blocked": True})
    if args.configure:
        print(spectrum.configure_measurement(center_freq=2.45e9, dry_run=dry))
    if args.sweep:
        print(spectrum.trigger_single_sweep(dry_run=dry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
