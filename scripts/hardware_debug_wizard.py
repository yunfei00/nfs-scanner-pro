#!/usr/bin/env python3
"""硬件调试向导 — Mock / Fake / Real 模式说明与离线检查。"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.devices.hardware_mode import (  # noqa: E402
    get_hardware_mode,
    hardware_mode_label,
)
from nfs_scanner_pro.devices.real.hardware_config import is_real_hardware_enabled


def _print_default_help() -> None:
    mode = get_hardware_mode()
    print(f"当前硬件模式：{mode.value}")
    print(f"真实硬件启用：{str(is_real_hardware_enabled()).lower()}")
    print("")
    print("可用调试命令：")
    print("  1. 运动平台状态：")
    print("     python scripts/debug_real_motion.py --status --fake")
    print("  2. 频谱仪 IDN：")
    print("     python scripts/debug_real_spectrum.py --idn --fake")
    print("  3. 相机枚举：")
    print("     python scripts/debug_real_camera.py --list --fake")
    print("  4. 舵机状态：")
    print("     python scripts/debug_real_servo.py --state --fake")
    print("  5. 离线扫描 fake-run：")
    print("     python scripts/run_real_scan_offline.py --fake-run")
    print("")
    print("真实硬件调试前请设置：")
    print("  NFS_HARDWARE_MODE=real")
    print("  NFS_ENABLE_REAL_HARDWARE=1")
    print("")
    print("详细说明见 docs/hardware-debug-guide.md")


def _run_script(name: str, args: list[str]) -> int:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=os.environ.copy(),
    )
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    return proc.returncode


def cmd_fake_check() -> int:
    print("Fake 检查（不连接真实设备）")
    print("")
    checks = [
        ("debug_real_motion.py", ["--status", "--fake"]),
        ("debug_real_spectrum.py", ["--idn", "--fake"]),
        ("debug_real_camera.py", ["--list", "--fake"]),
        ("debug_real_servo.py", ["--state", "--fake"]),
    ]
    ok = True
    for script, args in checks:
        code = _run_script(script, args)
        ok = ok and code == 0
    print("")
    code = _run_script("run_real_scan_offline.py", ["--fake-run"])
    return 0 if ok and code == 0 else 1


def cmd_real_check() -> int:
    if not is_real_hardware_enabled():
        print("拒绝：未设置 NFS_ENABLE_REAL_HARDWARE=1")
        print("真实硬件检查仅允许在安全开关启用后执行。")
        return 1
    from nfs_scanner_pro.devices.real import RealDeviceManager

    print(f"当前硬件模式：{hardware_mode_label(get_hardware_mode())}")
    print("Real 安全探测（不运动 / 不 sweep / 不拍照 / 不切舵机）")
    manager = RealDeviceManager()
    try:
        result = manager.test_all_safe()
        if result.get("status") == "disabled":
            print(result.get("message", "disabled"))
            return 0
        for key, value in sorted(result.items()):
            print(f"  {key}: {value}")
        return 0
    finally:
        manager.disconnect_all()


def cmd_show_env() -> None:
    keys = sorted(
        k
        for k in os.environ
        if k.startswith("NFS_")
    )
    print(f"当前硬件模式：{get_hardware_mode().value}")
    print(f"真实硬件启用：{is_real_hardware_enabled()}")
    print("")
    for key in keys:
        print(f"{key}={os.environ[key]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="硬件调试向导")
    parser.add_argument("--show-env", action="store_true")
    parser.add_argument("--fake-check", action="store_true")
    parser.add_argument("--real-check", action="store_true")
    args = parser.parse_args()

    if args.show_env:
        cmd_show_env()
        return 0
    if args.fake_check:
        return cmd_fake_check()
    if args.real_check:
        return cmd_real_check()

    _print_default_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
