"""扫描计划持久化 — Release 042 JSON / CSV / summary。"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from nfs_scanner_pro.app_paths import get_runtime_dir
from nfs_scanner_pro.scan.real_scan_plan import (
    CSV_POINT_FIELDS,
    ScanPlanPoint,
    SmallAreaScanPlan,
)


def _plans_base_dir() -> Path:
    return get_runtime_dir() / "scan_plans"


def _plan_dir(plan_id: str) -> Path:
    return _plans_base_dir() / plan_id


def _compute_ranges(plan: SmallAreaScanPlan) -> dict[str, Any]:
    xs = [point.x for point in plan.points]
    ys = [point.y for point in plan.points]
    zs = [point.z for point in plan.points]
    return {
        "x_range": [min(xs), max(xs)] if xs else [0.0, 0.0],
        "y_range": [min(ys), max(ys)] if ys else [0.0, 0.0],
        "z_range": [min(zs), max(zs)] if zs else [0.0, 0.0],
    }


def build_summary(plan: SmallAreaScanPlan, validation_result: dict[str, Any]) -> dict[str, Any]:
    ranges = _compute_ranges(plan)
    return {
        "plan_id": plan.plan_id,
        "point_count": plan.point_count(),
        "valid": validation_result.get("valid", False),
        "dry_run": plan.dry_run,
        "safe_mode": plan.safe_mode,
        "x_range": ranges["x_range"],
        "y_range": ranges["y_range"],
        "z_range": ranges["z_range"],
        "frequency": plan.frequency,
        "trace": plan.trace,
        "validation_summary": validation_result.get("summary", ""),
    }


def save_scan_plan(
    plan: SmallAreaScanPlan,
    validation_result: dict[str, Any],
    *,
    base_dir: Path | None = None,
) -> dict[str, Path]:
    """保存 scan_plan.json / scan_plan.csv / scan_plan_summary.json。"""
    directory = base_dir if base_dir is not None else _plan_dir(plan.plan_id)
    directory.mkdir(parents=True, exist_ok=True)

    json_path = directory / "scan_plan.json"
    csv_path = directory / "scan_plan.csv"
    summary_path = directory / "scan_plan_summary.json"

    payload = plan.as_dict()
    payload["point_count"] = plan.point_count()
    payload["validation"] = validation_result
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_POINT_FIELDS)
        writer.writeheader()
        for row in plan.to_csv_rows():
            writer.writerow(row)

    summary = build_summary(plan, validation_result)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "json_path": json_path,
        "csv_path": csv_path,
        "summary_path": summary_path,
    }


def _point_from_dict(data: dict[str, Any]) -> ScanPlanPoint:
    return ScanPlanPoint(
        index=int(data["index"]),
        row=int(data["row"]),
        col=int(data["col"]),
        x=float(data["x"]),
        y=float(data["y"]),
        z=float(data["z"]),
        frequency=str(data.get("frequency", "")),
        trace=str(data.get("trace", "")),
        dwell_ms=int(data.get("dwell_ms", 100)),
        sample_enabled=bool(data.get("sample_enabled", True)),
        motion_required=bool(data.get("motion_required", True)),
        safe_checked=bool(data.get("safe_checked", False)),
    )


def _plan_from_dict(data: dict[str, Any]) -> SmallAreaScanPlan:
    points = [_point_from_dict(item) for item in data.get("points", [])]
    return SmallAreaScanPlan(
        plan_id=str(data["plan_id"]),
        project_name=str(data.get("project_name", "")),
        region_name=str(data.get("region_name", "")),
        origin_x=float(data.get("origin_x", 0.0)),
        origin_y=float(data.get("origin_y", 0.0)),
        origin_z=float(data.get("origin_z", 0.0)),
        step_x=float(data.get("step_x", 0.0)),
        step_y=float(data.get("step_y", 0.0)),
        rows=int(data.get("rows", 3)),
        cols=int(data.get("cols", 3)),
        frequency=str(data.get("frequency", "")),
        trace=str(data.get("trace", "")),
        points=points,
        created_at=str(data.get("created_at", "")),
        dry_run=bool(data.get("dry_run", True)),
        safe_mode=bool(data.get("safe_mode", True)),
    )


def load_scan_plan(plan_id_or_path: str | Path) -> dict[str, Any]:
    """从 plan_id 或 JSON 文件路径加载计划。"""
    path = Path(plan_id_or_path)
    if path.is_file():
        json_path = path
    else:
        json_path = _plan_dir(str(plan_id_or_path)) / "scan_plan.json"
    if not json_path.is_file():
        return {"ok": False, "error": f"计划不存在: {json_path}"}
    data = json.loads(json_path.read_text(encoding="utf-8"))
    plan = _plan_from_dict(data)
    return {
        "ok": True,
        "plan": plan,
        "validation": data.get("validation", {}),
        "json_path": json_path,
    }


def list_scan_plans() -> list[str]:
    """列出已保存的 plan_id。"""
    base = _plans_base_dir()
    if not base.is_dir():
        return []
    return sorted(
        child.name
        for child in base.iterdir()
        if child.is_dir() and (child / "scan_plan.json").is_file()
    )
