"""真实小区域扫描计划 — Release 042 dry-run 路径规划。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

# 3x3 蛇形顺序：(offset_row, offset_col)
_SERPENTINE_OFFSETS: tuple[tuple[int, int], ...] = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
    (0, 0),
    (0, -1),
    (1, -1),
    (1, 0),
    (1, 1),
)

CSV_POINT_FIELDS = (
    "index",
    "row",
    "col",
    "x",
    "y",
    "z",
    "frequency",
    "trace",
    "dwell_ms",
    "sample_enabled",
    "motion_required",
    "safe_checked",
)


@dataclass
class ScanPlanPoint:
    index: int
    row: int
    col: int
    x: float
    y: float
    z: float
    frequency: str
    trace: str
    dwell_ms: int = 100
    sample_enabled: bool = True
    motion_required: bool = True
    safe_checked: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SmallAreaScanPlan:
    plan_id: str
    project_name: str
    region_name: str
    origin_x: float
    origin_y: float
    origin_z: float
    step_x: float
    step_y: float
    rows: int
    cols: int
    frequency: str
    trace: str
    points: list[ScanPlanPoint] = field(default_factory=list)
    created_at: str = ""
    dry_run: bool = True
    safe_mode: bool = True

    def point_count(self) -> int:
        return len(self.points)

    def as_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "project_name": self.project_name,
            "region_name": self.region_name,
            "origin_x": self.origin_x,
            "origin_y": self.origin_y,
            "origin_z": self.origin_z,
            "step_x": self.step_x,
            "step_y": self.step_y,
            "rows": self.rows,
            "cols": self.cols,
            "frequency": self.frequency,
            "trace": self.trace,
            "points": [point.as_dict() for point in self.points],
            "created_at": self.created_at,
            "dry_run": self.dry_run,
            "safe_mode": self.safe_mode,
        }

    def to_csv_rows(self) -> list[dict[str, Any]]:
        return [point.as_dict() for point in self.points]


def generate_3x3_scan_plan(
    *,
    project_name: str = "Manual_Check",
    region_name: str = "SmallArea_3x3",
    center_x: float = 50.0,
    center_y: float = -50.0,
    z: float = 5.0,
    step_mm: float = 0.5,
    frequency: str = "2.450 GHz",
    trace: str = "Trace 1",
    dwell_ms: int = 100,
) -> SmallAreaScanPlan:
    """生成 3x3 蛇形扫描计划，不执行运动或采样。"""
    plan_id = f"SP3x3-{uuid4().hex[:8].upper()}"
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    points: list[ScanPlanPoint] = []
    for index, (offset_row, offset_col) in enumerate(_SERPENTINE_OFFSETS):
        grid_row = offset_row + 1
        grid_col = offset_col + 1
        points.append(
            ScanPlanPoint(
                index=index,
                row=grid_row,
                col=grid_col,
                x=round(center_x + offset_col * step_mm, 6),
                y=round(center_y + offset_row * step_mm, 6),
                z=round(z, 6),
                frequency=frequency,
                trace=trace,
                dwell_ms=dwell_ms,
                sample_enabled=True,
                motion_required=True,
                safe_checked=False,
            )
        )
    return SmallAreaScanPlan(
        plan_id=plan_id,
        project_name=project_name,
        region_name=region_name,
        origin_x=center_x,
        origin_y=center_y,
        origin_z=z,
        step_x=step_mm,
        step_y=step_mm,
        rows=3,
        cols=3,
        frequency=frequency,
        trace=trace,
        points=points,
        created_at=created_at,
        dry_run=True,
        safe_mode=True,
    )
