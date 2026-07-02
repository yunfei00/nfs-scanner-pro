"""逐点手动确认扫描会话 — Release 043。"""

from __future__ import annotations

import math
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from nfs_scanner_pro.scan.real_scan_plan import SmallAreaScanPlan

DEFAULT_POSITION_TOLERANCE_MM = 0.2
POINT_STATUSES = frozenset({"pending", "sampled", "skipped", "failed"})


def get_position_tolerance_mm() -> float:
    return float(
        os.environ.get(
            "NFS_MANUAL_SCAN_POSITION_TOLERANCE_MM",
            str(DEFAULT_POSITION_TOLERANCE_MM),
        )
    )


@dataclass
class ManualScanPointStatus:
    index: int
    row: int
    col: int
    planned_x: float
    planned_y: float
    planned_z: float
    status: str = "pending"
    sample_id: str = ""
    sample_path: str = ""
    actual_x: float | None = None
    actual_y: float | None = None
    actual_z: float | None = None
    position_error_mm: float | None = None
    frequency_hz: float | None = None
    amplitude_dbm: float | None = None
    sampled_at: str = ""
    message: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ManualScanSession:
    session_id: str
    plan_id: str
    project_name: str
    region_name: str
    created_at: str
    updated_at: str
    dry_run: bool
    safe_mode: bool
    position_tolerance_mm: float
    points: list[ManualScanPointStatus] = field(default_factory=list)

    def point_count(self) -> int:
        return len(self.points)

    def sampled_count(self) -> int:
        return sum(1 for point in self.points if point.status == "sampled")

    def pending_count(self) -> int:
        return sum(1 for point in self.points if point.status == "pending")

    def failed_count(self) -> int:
        return sum(1 for point in self.points if point.status == "failed")

    def completion_ratio(self) -> float:
        total = self.point_count()
        if total == 0:
            return 0.0
        return round(self.sampled_count() / total, 4)

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "plan_id": self.plan_id,
            "project_name": self.project_name,
            "region_name": self.region_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "dry_run": self.dry_run,
            "safe_mode": self.safe_mode,
            "position_tolerance_mm": self.position_tolerance_mm,
            "points": [point.as_dict() for point in self.points],
        }


def create_manual_scan_session(plan: SmallAreaScanPlan) -> ManualScanSession:
    """从 3x3 扫描计划创建手动采样会话，不连接设备、不采样。"""
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    session_id = f"MS-{uuid4().hex[:8].upper()}"
    tolerance = get_position_tolerance_mm()
    points = [
        ManualScanPointStatus(
            index=point.index,
            row=point.row,
            col=point.col,
            planned_x=point.x,
            planned_y=point.y,
            planned_z=point.z,
            status="pending",
        )
        for point in plan.points
    ]
    return ManualScanSession(
        session_id=session_id,
        plan_id=plan.plan_id,
        project_name=plan.project_name,
        region_name=plan.region_name,
        created_at=now,
        updated_at=now,
        dry_run=plan.dry_run,
        safe_mode=True,
        position_tolerance_mm=tolerance,
        points=points,
    )


def _point_from_dict(data: dict[str, Any]) -> ManualScanPointStatus:
    return ManualScanPointStatus(
        index=int(data["index"]),
        row=int(data["row"]),
        col=int(data["col"]),
        planned_x=float(data["planned_x"]),
        planned_y=float(data["planned_y"]),
        planned_z=float(data["planned_z"]),
        status=str(data.get("status", "pending")),
        sample_id=str(data.get("sample_id", "")),
        sample_path=str(data.get("sample_path", "")),
        actual_x=data.get("actual_x"),
        actual_y=data.get("actual_y"),
        actual_z=data.get("actual_z"),
        position_error_mm=data.get("position_error_mm"),
        frequency_hz=data.get("frequency_hz"),
        amplitude_dbm=data.get("amplitude_dbm"),
        sampled_at=str(data.get("sampled_at", "")),
        message=str(data.get("message", "")),
    )


def session_from_dict(data: dict[str, Any]) -> ManualScanSession:
    points = [_point_from_dict(item) for item in data.get("points", [])]
    return ManualScanSession(
        session_id=str(data["session_id"]),
        plan_id=str(data["plan_id"]),
        project_name=str(data.get("project_name", "")),
        region_name=str(data.get("region_name", "")),
        created_at=str(data.get("created_at", "")),
        updated_at=str(data.get("updated_at", "")),
        dry_run=bool(data.get("dry_run", True)),
        safe_mode=bool(data.get("safe_mode", True)),
        position_tolerance_mm=float(
            data.get("position_tolerance_mm", DEFAULT_POSITION_TOLERANCE_MM)
        ),
        points=points,
    )


def load_manual_scan_session(path: str | Any) -> ManualScanSession:
    """从 JSON 文件路径加载会话。"""
    from pathlib import Path

    json_path = Path(path)
    import json

    data = json.loads(json_path.read_text(encoding="utf-8"))
    return session_from_dict(data)


def get_next_pending_point(session: ManualScanSession) -> ManualScanPointStatus | None:
    for point in session.points:
        if point.status == "pending":
            return point
    return None


def validate_position_near_plan_point(
    planned: dict[str, Any],
    actual: dict[str, Any],
    tolerance_mm: float,
) -> dict[str, Any]:
    """校验实际位置是否接近计划点，不连接设备。"""
    try:
        px = float(planned["x"])
        py = float(planned["y"])
        pz = float(planned["z"])
        ax = float(actual["x"])
        ay = float(actual["y"])
        az = float(actual["z"])
    except (KeyError, TypeError, ValueError):
        return {
            "ok": False,
            "error_mm": None,
            "dx": None,
            "dy": None,
            "dz": None,
            "reason": "实际位置缺少有效 x/y/z 字段",
        }

    dx = ax - px
    dy = ay - py
    dz = az - pz
    error_mm = math.sqrt(dx * dx + dy * dy + dz * dz)
    ok = error_mm <= tolerance_mm
    return {
        "ok": ok,
        "error_mm": round(error_mm, 6),
        "dx": round(dx, 6),
        "dy": round(dy, 6),
        "dz": round(dz, 6),
        "reason": "" if ok else f"位置误差 {error_mm:.3f} mm 超过容差 {tolerance_mm} mm",
    }


def update_point_sample(
    session: ManualScanSession,
    point_index: int,
    sample_record: dict[str, Any],
    validation_result: dict[str, Any],
) -> dict[str, Any]:
    """更新指定点的采样结果。"""
    target: ManualScanPointStatus | None = None
    for point in session.points:
        if point.index == point_index:
            target = point
            break
    if target is None:
        return {"ok": False, "error": f"点 index={point_index} 不存在"}

    position = sample_record.get("position", {})
    spectrum = sample_record.get("spectrum", {})
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    if validation_result.get("ok") is True:
        target.status = "sampled"
        target.actual_x = float(position.get("x", target.planned_x))
        target.actual_y = float(position.get("y", target.planned_y))
        target.actual_z = float(position.get("z", target.planned_z))
        target.position_error_mm = validation_result.get("error_mm")
        target.frequency_hz = spectrum.get("frequency_hz")
        target.amplitude_dbm = spectrum.get("amplitude_dbm")
        target.sample_id = str(sample_record.get("sample_id", ""))
        target.sample_path = str(sample_record.get("sample_path", ""))
        target.sampled_at = str(sample_record.get("timestamp_iso", now))
        target.message = ""
    else:
        target.status = "failed"
        target.message = str(
            validation_result.get("reason", validation_result.get("error", "位置校验失败"))
        )
        if position:
            try:
                target.actual_x = float(position.get("x"))
                target.actual_y = float(position.get("y"))
                target.actual_z = float(position.get("z"))
            except (TypeError, ValueError):
                pass
        target.position_error_mm = validation_result.get("error_mm")

    session.updated_at = now
    return {"ok": True, "point": target.as_dict()}
