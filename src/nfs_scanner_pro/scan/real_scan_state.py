"""真实扫描状态 — Release 044。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class RealScanState(str, Enum):
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RealScanProgress:
    task_id: str
    plan_id: str
    total_points: int
    current_index: int
    completed_points: int
    failed_points: int
    state: str
    message: str
    started_at: str
    updated_at: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
