"""设备快照 — Release 018。"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def build_device_snapshot(
    motion: dict[str, Any],
    spectrum: dict[str, Any],
    camera: dict[str, Any],
    servo: dict[str, Any],
) -> dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "motion": motion,
        "spectrum": spectrum,
        "camera": camera,
        "servo": servo,
    }
