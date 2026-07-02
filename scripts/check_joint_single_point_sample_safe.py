#!/usr/bin/env python3
"""真实联合单点采样 — 当前位置 + Marker 幅度，不运动、不 sweep。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.devices.real import (  # noqa: E402
    RealDeviceManager,
    is_real_hardware_enabled,
    load_hardware_config,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="真实联合单点采样（不运动 / 不 sweep）")
    parser.add_argument(
        "--save",
        action="store_true",
        help="保存 JSON / CSV 单点样本",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="只读取并打印，不保存",
    )
    args = parser.parse_args()
    save = args.save and not args.no_save

    if not is_real_hardware_enabled():
        print("真实设备未启用。")
        print("如需安全联合采样，请设置 NFS_ENABLE_REAL_HARDWARE=1")
        print("")
        print("Windows PowerShell 示例：")
        print('  $env:NFS_ENABLE_REAL_HARDWARE="1"')
        print('  $env:NFS_MOTION_PORT="COM6"')
        print('  $env:NFS_MOTION_BAUDRATE="115200"')
        print('  $env:NFS_SPECTRUM_BACKEND="socket"')
        print('  $env:NFS_SPECTRUM_HOST="192.168.1.100"')
        print('  $env:NFS_SPECTRUM_PORT="5025"')
        print("  python scripts/check_joint_single_point_sample_safe.py --save")
        return 0

    config = load_hardware_config()
    manager = RealDeviceManager(config)
    print(f"Real hardware enabled: {is_real_hardware_enabled()}")
    print(f"Motion port: {config.motion.port}")
    print(f"Spectrum backend: {config.spectrum.backend}")
    print(f"Spectrum address: {config.spectrum.address}")
    print("联合单点采样（不运动 / 不 sweep / 不改仪表配置）")
    print(f"Save samples: {'yes' if save else 'no'}")
    print("")

    exit_code = 0
    try:
        result = manager.sample_single_point_safe(save=save)
        if result.get("disabled"):
            print(f"Joint sample disabled: {result.get('error', '')}")
            return 0

        motion_pos = result.get("motion_position", {})
        marker = result.get("spectrum_marker", {})
        record = result.get("record", {})

        print(f"Motion state: {motion_pos.get('state', '')}")
        if motion_pos.get("ok"):
            print(
                "Motion position: "
                f"X={motion_pos.get('x', 0):.3f} "
                f"Y={motion_pos.get('y', 0):.3f} "
                f"Z={motion_pos.get('z', 0):.3f} "
                f"({motion_pos.get('source', '')})"
            )
        else:
            print(f"Motion position: FAIL — {motion_pos.get('error', '')}")
            exit_code = 1

        freq_hz = marker.get("frequency_hz")
        freq_ghz = marker.get("frequency_ghz")
        if freq_ghz is not None:
            print(f"Spectrum frequency: {freq_ghz:.6g} GHz ({freq_hz} Hz)")
        elif marker.get("ok"):
            print("Spectrum frequency: —")
        else:
            print(f"Spectrum frequency: FAIL — {marker.get('error', '')}")

        if marker.get("ok"):
            print(
                f"Spectrum amplitude: {marker.get('amplitude_dbm')} "
                f"{marker.get('unit', 'dBm')}"
            )
            print(f"Raw response: {marker.get('raw', '')}")
        else:
            print(f"Spectrum amplitude: FAIL — {marker.get('error', '')}")
            exit_code = 1

        if save and result.get("ok"):
            print(f"Sample JSON path: {result.get('json_path', '')}")
            print(f"Sample CSV path: {result.get('csv_path', '')}")

        print(f"Motion command executed: {record.get('motion_command_executed', False)}")
        print(f"Sweep started: {record.get('sweep_started', False)}")

        if not result.get("ok"):
            print(f"Joint sample: FAIL — {result.get('error', '')}")
            exit_code = 1
        else:
            print("Joint sample: PASS")
    except Exception as exc:  # noqa: BLE001
        print(f"联合采样失败：{exc}")
        exit_code = 1
    finally:
        manager.disconnect_all()
        print("Disconnect done")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
