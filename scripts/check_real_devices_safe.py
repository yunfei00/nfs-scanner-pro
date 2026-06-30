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
)


def main() -> int:
    if not is_real_hardware_enabled():
        print("真实设备未启用。")
        print("如需安全探测，请设置：")
        print("  NFS_ENABLE_REAL_HARDWARE=1")
        print("")
        print("Windows PowerShell 示例：")
        print('  $env:NFS_ENABLE_REAL_HARDWARE="1"')
        print("  python scripts/check_real_devices_safe.py")
        return 0

    manager = RealDeviceManager()
    print("真实设备安全探测开始（不运动 / 不扫描 / 不控制舵机）")
    print("")

    try:
        results = manager.test_all_safe()
        for key, value in results.items():
            print(f"[{key}] {value}")
        print("")
        print("探测完成。")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"探测失败：{exc}")
        return 1
    finally:
        disconnect = manager.disconnect_all()
        for key, value in disconnect.items():
            print(f"[disconnect:{key}] {value}")


if __name__ == "__main__":
    raise SystemExit(main())
