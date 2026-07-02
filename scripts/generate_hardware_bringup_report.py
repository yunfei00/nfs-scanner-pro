#!/usr/bin/env python3
"""生成真实硬件联调准备诊断报告 — Release 047（离线，不连接设备）。"""

from __future__ import annotations

import importlib.util
import inspect
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.app_paths import get_runtime_dir  # noqa: E402
from nfs_scanner_pro.devices.hardware_mode import get_hardware_mode  # noqa: E402
from nfs_scanner_pro.devices.real.camera_adapter import CameraAdapter  # noqa: E402
from nfs_scanner_pro.devices.real.hardware_config import (  # noqa: E402
    get_all_safety_flags,
    get_config_source_summary,
    get_scan_config,
    is_real_hardware_enabled,
    load_hardware_config,
)
from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter  # noqa: E402
from nfs_scanner_pro.devices.real.real_device_manager import RealDeviceManager  # noqa: E402
from nfs_scanner_pro.devices.real.servo_adapter import ServoAdapter  # noqa: E402
from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter  # noqa: E402

DOCS = (
    "docs/hardware/README.md",
    "docs/hardware/motion-platform-bringup.md",
    "docs/hardware/spectrum-analyzer-bringup.md",
    "docs/hardware/camera-bringup.md",
    "docs/hardware/servo-bringup.md",
    "docs/hardware/real-scan-bringup.md",
    "docs/hardware/hardware-safety-switches.md",
    "docs/hardware/hardware-debug-command-map.md",
    "docs/hardware/hardware-troubleshooting.md",
    "docs/hardware-debug-guide.md",
)

CLI_TOOLS = {
    "debug_real_motion.py": {
        "default_connects": False,
        "fake_flag": "--fake",
        "real_requires": ["NFS_ENABLE_REAL_HARDWARE=1"],
        "example": "python scripts/debug_real_motion.py --status --fake",
    },
    "debug_real_spectrum.py": {
        "default_connects": False,
        "fake_flag": "--fake",
        "real_requires": ["NFS_ENABLE_REAL_HARDWARE=1"],
        "example": "python scripts/debug_real_spectrum.py --idn --fake",
    },
    "debug_real_camera.py": {
        "default_connects": False,
        "fake_flag": "--fake",
        "real_requires": ["NFS_ENABLE_REAL_CAMERA=1"],
        "example": "python scripts/debug_real_camera.py --list --fake",
    },
    "debug_real_servo.py": {
        "default_connects": False,
        "fake_flag": "--fake",
        "real_requires": ["NFS_ENABLE_REAL_SERVO=1"],
        "example": "python scripts/debug_real_servo.py --state --fake",
    },
    "hardware_debug_wizard.py": {
        "default_connects": False,
        "fake_flag": "--fake-check",
        "real_requires": ["NFS_ENABLE_REAL_HARDWARE=1"],
        "example": "python scripts/hardware_debug_wizard.py",
    },
    "run_real_scan_offline.py": {
        "default_connects": False,
        "fake_flag": "--fake-run",
        "real_requires": ["NFS_ENABLE_REAL_SCAN_EXECUTION=1"],
        "example": "python scripts/run_real_scan_offline.py --fake-run",
    },
    "generate_hardware_bringup_report.py": {
        "default_connects": False,
        "fake_flag": "N/A",
        "real_requires": [],
        "example": "python scripts/generate_hardware_bringup_report.py",
    },
    "check_hardware_interface_inventory.py": {
        "default_connects": False,
        "fake_flag": "N/A",
        "real_requires": [],
        "example": "python scripts/check_hardware_interface_inventory.py",
    },
}

NEXT_STEPS = [
    "1. 复制 config/hardware.local.example.yaml 为 config/hardware.local.yaml",
    "2. 设置 NFS_HARDWARE_MODE=mock，运行 check_hardware_interface_inventory.py",
    "3. 不接设备：fake-run 扫描 python scripts/run_real_scan_offline.py --fake-run",
    "4. 接运动平台：仅 status 查询（NFS_ENABLE_REAL_HARDWARE=1）",
    "5. 接频谱仪：仅 IDN / marker（不 sweep）",
    "6. 接相机：仅 --list 枚举",
    "7. 接舵机：仅 --state 查询",
    "8. UI 真实扫描控制台：dry-run → fake-run",
    "9. 全部子开关确认后再考虑 real-run",
]


def _report_dir() -> Path:
    runtime = get_runtime_dir()
    if "verification" in runtime.parts and runtime.name.startswith("R"):
        directory = runtime
    else:
        directory = runtime / "hardware_reports"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _run_inventory() -> dict:
    spec = importlib.util.spec_from_file_location(
        "check_inventory",
        SCRIPTS / "check_hardware_interface_inventory.py",
    )
    if spec is None or spec.loader is None:
        return {"ok": False, "error": "inventory script missing"}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_hardware_interface_inventory.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {"ok": proc.returncode == 0, "stdout": proc.stdout}


def _adapter_snapshots() -> dict:
    motion = MotionGrblAdapter()
    spectrum = SpectrumScpiAdapter()
    camera = CameraAdapter()
    servo = ServoAdapter()
    manager = RealDeviceManager()
    return {
        "motion": motion.snapshot(),
        "spectrum": spectrum.snapshot(),
        "camera": camera.snapshot(),
        "servo": servo.snapshot(),
        "manager": manager.get_snapshot(),
    }


def _mode_comparison() -> list[dict[str, str]]:
    return [
        {
            "mode": "Mock",
            "connects_device": "否",
            "motion": "MockDeviceManager",
            "scan": "ScanEngineMock",
            "use_case": "UI 演示 / 回归",
        },
        {
            "mode": "Fake / DryRun",
            "connects_device": "否（FakeTransport）",
            "motion": "Fake 命令链路",
            "scan": "RealScanExecutor fake-run / dry-run",
            "use_case": "离线流程验证",
        },
        {
            "mode": "Real",
            "connects_device": "是（需 NFS_ENABLE_REAL_*）",
            "motion": "GRBL 串口",
            "scan": "RealScanExecutor real-run（默认 blocked）",
            "use_case": "现场联调",
        },
    ]


def build_report() -> dict:
    cfg = load_hardware_config()
    snapshots = _adapter_snapshots()
    inventory = _run_inventory()
    docs_status = {doc: (ROOT / doc).is_file() for doc in DOCS}
    return {
        "timestamp_iso": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "hardware_mode": get_hardware_mode().value,
        "real_hardware_enabled": is_real_hardware_enabled(),
        "config_source": get_config_source_summary(),
        "hardware_config": {
            "hardware_mode": cfg.hardware_mode,
            "scan": get_scan_config(),
        },
        "safety_flags": get_all_safety_flags(),
        "interface_inventory": inventory,
        "adapter_snapshots": snapshots,
        "cli_tools": CLI_TOOLS,
        "docs": docs_status,
        "mode_comparison": _mode_comparison(),
        "next_manual_steps": NEXT_STEPS,
    }


def _render_markdown(report: dict) -> str:
    lines = [
        "# 硬件联调准备诊断报告",
        "",
        f"- 生成时间：{report['timestamp_iso']}",
        f"- 当前模式：**{report['hardware_mode']}**",
        f"- 真实硬件启用：**{report['real_hardware_enabled']}**",
        "",
        "## 安全开关状态",
        "",
    ]
    for key, value in sorted(report["safety_flags"].items()):
        lines.append(f"- `{key}` = {value}")
    lines.extend(
        [
            "",
            "## 配置来源",
            "",
            f"- yaml 路径：`{report['config_source'].get('yaml_path')}`",
            f"- yaml 状态：`{report['config_source'].get('yaml_status')}`",
            "",
            "## 接口完整性",
            "",
            f"- inventory ok: {report['interface_inventory'].get('ok')}",
            "",
            "## Mock / Fake / Real 对照",
            "",
            "| 模式 | 连接设备 | 用途 |",
            "|------|----------|------|",
        ]
    )
    for row in report["mode_comparison"]:
        lines.append(f"| {row['mode']} | {row['connects_device']} | {row['use_case']} |")
    lines.extend(["", "## CLI 调试命令", ""])
    for name, info in report["cli_tools"].items():
        lines.append(f"- `{info['example']}`")
    lines.extend(["", "## 后续真实设备调试顺序", ""])
    for step in report["next_manual_steps"]:
        lines.append(f"- {step}")
    lines.append("")
    lines.append("> 本报告离线生成，未连接真实设备。")
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    directory = _report_dir()
    json_path = directory / "hardware_bringup_report.json"
    md_path = directory / "hardware_bringup_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    print(f"Report JSON: {json_path}")
    print(f"Report MD:   {md_path}")
    print(f"hardware_mode: {report['hardware_mode']}")
    print(f"real_hardware_enabled: {report['real_hardware_enabled']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
