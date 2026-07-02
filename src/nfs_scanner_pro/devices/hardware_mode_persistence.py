"""硬件模式持久化 — Release 045。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from nfs_scanner_pro.app_paths import get_runtime_dir
from nfs_scanner_pro.devices.hardware_mode import HardwareMode, normalize_hardware_mode
from nfs_scanner_pro.devices.real.hardware_config import is_real_hardware_enabled

_MODE_FILE = "hardware_mode.json"


def _mode_path() -> Path:
    return get_runtime_dir() / _MODE_FILE


def save_hardware_mode(mode: str | HardwareMode) -> Path:
    normalized = normalize_hardware_mode(mode)
    payload = {
        "hardware_mode": normalized.value,
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "real_hardware_enabled": is_real_hardware_enabled(),
        "note": "Real hardware requires NFS_ENABLE_REAL_HARDWARE=1",
    }
    path = _mode_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_hardware_mode() -> HardwareMode:
    path = _mode_path()
    if not path.is_file():
        return HardwareMode.MOCK
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return normalize_hardware_mode(data.get("hardware_mode", "mock"))
    except Exception:  # noqa: BLE001
        return HardwareMode.MOCK


def load_hardware_mode_record() -> dict:
    path = _mode_path()
    if not path.is_file():
        return {
            "hardware_mode": HardwareMode.MOCK.value,
            "real_hardware_enabled": False,
            "note": "Real hardware requires NFS_ENABLE_REAL_HARDWARE=1",
        }
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"hardware_mode": HardwareMode.MOCK.value}


def reset_hardware_mode() -> Path:
    return save_hardware_mode(HardwareMode.MOCK)
