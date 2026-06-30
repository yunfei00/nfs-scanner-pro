"""扫描结果 Mock — Release 019。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

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

    @classmethod
    def create(
        cls,
        *,
        task_id: str,
        config: ScanTaskConfig,
        device_snapshot: dict[str, Any],
        final_index: int,
        status: str,
    ) -> ScanResultMock:
        now = datetime.now().isoformat(timespec="seconds")
        return cls(
            task_id=task_id,
            config=config,
            device_snapshot=device_snapshot,
            points=[{"final_index": final_index}],
            started_at=now,
            finished_at=now,
            status=status,
        )
