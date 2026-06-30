"""扫描结果 Mock — Release 019。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from nfs_scanner_pro.scan.scan_path_mock import ScanPathMock
from nfs_scanner_pro.scan.scan_point import ScanPointMock
from nfs_scanner_pro.scan.scan_task_config import ScanTaskConfig


@dataclass
class ScanResultMock:
    task_id: str
    config: ScanTaskConfig
    device_snapshot: dict[str, Any]
    points: list[dict[str, Any]] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    status: str = "completed"
    path: ScanPathMock | None = field(default=None, repr=False)
    preview_points: list[ScanPointMock] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        *,
        task_id: str,
        config: ScanTaskConfig,
        device_snapshot: dict[str, Any],
        final_index: int,
        status: str,
        path: ScanPathMock | None = None,
        started_at: str = "",
    ) -> ScanResultMock:
        finished_at = datetime.now().isoformat(timespec="seconds")
        if not started_at:
            started_at = finished_at
        return cls(
            task_id=task_id,
            config=config,
            device_snapshot=device_snapshot,
            points=[{"final_index": final_index}],
            started_at=started_at,
            finished_at=finished_at,
            status=status,
            path=path,
        )
