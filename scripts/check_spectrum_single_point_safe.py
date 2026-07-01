#!/usr/bin/env python3
"""真实频谱仪单点幅度安全读取 — 仅 Marker 查询，不改配置、不 sweep。"""

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
        print("如需安全读取频谱仪单点幅度，请设置 NFS_ENABLE_REAL_HARDWARE=1")
        print("")
        print("Windows PowerShell 示例：")
        print('  $env:NFS_ENABLE_REAL_HARDWARE="1"')
        print('  $env:NFS_SPECTRUM_BACKEND="socket"')
        print('  $env:NFS_SPECTRUM_HOST="192.168.1.100"')
        print('  $env:NFS_SPECTRUM_PORT="5025"')
        print("  python scripts/check_spectrum_single_point_safe.py")
        return 0

    config = load_hardware_config()
    manager = RealDeviceManager(config)
    print(f"Real hardware enabled: {is_real_hardware_enabled()}")
    print(f"Spectrum backend: {config.spectrum.backend}")
    print(f"Spectrum address: {config.spectrum.address}")
    print("频谱仪单点幅度安全读取（不 sweep / 不改配置 / 不读完整 Trace）")
    print("")

    exit_code = 0
    try:
        result = manager.spectrum.read_single_point_amplitude()
        connect_msg = str(result.get("connect", ""))
        if connect_msg:
            print(f"Spectrum connect: {_connect_result(connect_msg)} — {connect_msg}")
            if _connect_result(connect_msg) == "FAIL":
                exit_code = 1

        idn = result.get("idn", {})
        freq = result.get("frequency", {})
        print(f"IDN: {idn.get('idn', idn.get('error', ''))}")
        print(f"Current frequency: {_format_frequency(freq)}")

        if result.get("ok"):
            print(f"Marker amplitude: {result.get('amplitude_dbm')} {result.get('unit', 'dBm')}")
            print(f"Raw response: {result.get('raw', '')}")
            print(f"Source: {result.get('source', 'marker')}")
        else:
            marker = result.get("marker", {})
            print(
                "Marker amplitude: FAIL — "
                f"{result.get('error', marker.get('error', '未知错误'))}"
            )
            if marker.get("raw"):
                print(f"Raw response: {marker.get('raw')}")
            exit_code = 1
    except Exception as exc:  # noqa: BLE001
        print(f"读取失败：{exc}")
        exit_code = 1
    finally:
        if manager.spectrum.is_connected():
            manager.spectrum.disconnect()
        print("Disconnect done")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
