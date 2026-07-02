#!/usr/bin/env python3
"""真实设备安全探测 — 仅连接与查询，不运动、不扫描。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.devices.real import (  # noqa: E402
    RealDeviceManager,
    is_real_hardware_enabled,
    is_real_motion_jog_enabled,
    load_hardware_config,
)


def _connect_result(message: str) -> str:
    lowered = message.lower()
    if "已连接" in message or "connected" in lowered:
        return "PASS"
    if "未启用" in message or "disabled" in lowered:
        return "SKIP"
    return "FAIL"


def _format_frequency(freq: dict) -> str:
    if not freq.get("ok"):
        return f"FAIL — {freq.get('error', '')}"
    ghz = freq.get("frequency_ghz")
    hz = freq.get("frequency_hz")
    if ghz is not None:
        return f"{ghz:.6g} GHz ({hz} Hz)"
    return str(freq.get("raw", ""))


def main() -> int:
    if not is_real_hardware_enabled():
        print("真实设备未启用。")
        print("如需安全探测，请设置：")
        print("  NFS_ENABLE_REAL_HARDWARE=1")
        print("")
        print("Windows PowerShell 示例：")
        print('  $env:NFS_ENABLE_REAL_HARDWARE="1"')
        print('  $env:NFS_SPECTRUM_BACKEND="socket"')
        print('  $env:NFS_SPECTRUM_HOST="192.168.1.100"')
        print('  $env:NFS_SPECTRUM_PORT="5025"')
        print('  $env:NFS_MOTION_PORT="COM6"')
        print("  python scripts/check_real_devices_safe.py")
        return 0

    config = load_hardware_config()
    manager = RealDeviceManager(config)
    print(f"Real hardware enabled: {is_real_hardware_enabled()}")
    print(f"Spectrum backend: {config.spectrum.backend}")
    print(f"Spectrum address: {config.spectrum.address}")
    print(f"Motion port: {config.motion.port}")
    if is_real_motion_jog_enabled():
        print(
            "真实点动已开启，但本脚本不会执行点动。"
            "如需手动点动，请使用 scripts/manual_motion_jog_safe.py"
        )
    print("真实设备安全探测开始（不运动 / 不扫描 / 不改仪表配置）")
    print("Joint single point sample: available（请使用 scripts/check_joint_single_point_sample_safe.py）")
    print("")

    exit_code = 0
    try:
        spectrum_connect_msg = manager.spectrum.connect()
        spectrum_connect_status = _connect_result(spectrum_connect_msg)
        print(f"Spectrum connect: {spectrum_connect_status} — {spectrum_connect_msg}")
        if spectrum_connect_status == "FAIL":
            exit_code = 1

        if manager.spectrum.is_connected():
            idn = manager.spectrum.query_idn()
            syst_err = manager.spectrum.query_system_error()
            freq = manager.spectrum.get_current_frequency()
            trace = manager.spectrum.read_trace_info()
            marker = manager.spectrum.read_marker_amplitude()

            print(f"Spectrum *IDN?: {idn.get('idn', idn.get('error', ''))}")
            print(
                "Spectrum SYST:ERR?: "
                f"{syst_err.get('error_text', syst_err.get('error', ''))}"
            )
            print(f"Spectrum current frequency: {_format_frequency(freq)}")
            if trace.get("ok"):
                print(f"Spectrum trace info: {trace.get('traces', [])}")
            else:
                print(f"Spectrum trace info: FAIL — {trace.get('error', '')}")

            if marker.get("ok"):
                print("Spectrum single point amplitude: PASS")
                print(f"Spectrum amplitude_dbm: {marker.get('amplitude_dbm')} dBm")
                print(f"Spectrum marker raw: {marker.get('raw', '')}")
            else:
                print(
                    "Spectrum single point amplitude: FAIL — "
                    f"{marker.get('error', '')}"
                )

        motion_connect_msg = manager.motion.connect()
        motion_connect_status = _connect_result(motion_connect_msg)
        print(f"Motion connect: {motion_connect_status} — {motion_connect_msg}")
        if motion_connect_status == "FAIL":
            exit_code = 1

        if manager.motion.is_connected():
            status = manager.motion.query_status()
            position = manager.motion.refresh_position()
            if isinstance(status, dict):
                print(f"Motion status raw: {status.get('raw', '')}")
                print(f"Motion state: {status.get('state', '')}")
            if isinstance(position, dict) and position.get("ok"):
                print(
                    "Motion position: "
                    f"X={position.get('x', 0):.3f} "
                    f"Y={position.get('y', 0):.3f} "
                    f"Z={position.get('z', 0):.3f} "
                    f"({position.get('source', '')})"
                )
            elif isinstance(position, dict):
                print(f"Motion position: FAIL — {position.get('error', '')}")
                exit_code = 1

        print("")
        print("探测完成。")
    except Exception as exc:  # noqa: BLE001
        print(f"探测失败：{exc}")
        exit_code = 1
    finally:
        disconnect = manager.disconnect_all()
        print("Disconnect done")
        for key, value in disconnect.items():
            print(f"  [{key}] {value}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
