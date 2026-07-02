"""真实扫描计划安全校验 — Release 042 软限位与计划约束。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from nfs_scanner_pro.devices.real.hardware_config import load_motion_safety_config
from nfs_scanner_pro.scan.real_scan_plan import ScanPlanPoint, SmallAreaScanPlan

_FORBIDDEN_PLAN_KEYS = frozenset(
    {
        "home",
        "move_to",
        "gcode",
        "g_code",
        "g0",
        "g1",
        "jog",
        "sweep",
    }
)


@dataclass
class ScanSafetyLimits:
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    max_points: int
    max_step_mm: float
    max_area_mm: float

    @classmethod
    def from_env(cls) -> ScanSafetyLimits:
        motion = load_motion_safety_config()
        return cls(
            x_min=motion.x_min,
            x_max=motion.x_max,
            y_min=motion.y_min,
            y_max=motion.y_max,
            z_min=motion.z_min,
            z_max=motion.z_max,
            max_points=int(os.environ.get("NFS_SCAN_MAX_POINTS", "9")),
            max_step_mm=float(os.environ.get("NFS_SCAN_MAX_STEP_MM", "1.0")),
            max_area_mm=float(os.environ.get("NFS_SCAN_MAX_AREA_MM", "5.0")),
        )


def validate_scan_point(
    x: float,
    y: float,
    z: float,
    *,
    limits: ScanSafetyLimits | None = None,
) -> dict[str, Any]:
    """检查单点坐标是否在软限位内。"""
    lim = limits or ScanSafetyLimits.from_env()
    try:
        xf = float(x)
        yf = float(y)
        zf = float(z)
    except (TypeError, ValueError):
        return {"ok": False, "reason": "坐标不是有效数字"}

    if xf < lim.x_min or xf > lim.x_max:
        return {"ok": False, "reason": f"x={xf} 超出软限位 [{lim.x_min}, {lim.x_max}]"}
    if yf < lim.y_min or yf > lim.y_max:
        return {"ok": False, "reason": f"y={yf} 超出软限位 [{lim.y_min}, {lim.y_max}]"}
    if zf < lim.z_min or zf > lim.z_max:
        return {"ok": False, "reason": f"z={zf} 超出软限位 [{lim.z_min}, {lim.z_max}]"}
    return {"ok": True, "reason": ""}


def _plan_has_forbidden_fields(plan: SmallAreaScanPlan) -> list[str]:
    hits: list[str] = []
    payload = plan.as_dict()
    for key in payload:
        if key.lower() in _FORBIDDEN_PLAN_KEYS:
            hits.append(key)
    for point in plan.points:
        for key in point.as_dict():
            if key.lower() in _FORBIDDEN_PLAN_KEYS:
                hits.append(f"point[{point.index}].{key}")
    return hits


def validate_scan_plan(
    plan: SmallAreaScanPlan,
    *,
    limits: ScanSafetyLimits | None = None,
) -> dict[str, Any]:
    """校验扫描计划点数、步长、软限位与区域跨度。"""
    lim = limits or ScanSafetyLimits.from_env()
    failed_points: list[dict[str, Any]] = []
    summary_parts: list[str] = []

    if plan.point_count() > lim.max_points:
        return {
            "ok": False,
            "valid": False,
            "failed_points": [],
            "summary": f"点数 {plan.point_count()} 超过上限 {lim.max_points}",
        }

    step = max(plan.step_x, plan.step_y)
    if step > lim.max_step_mm:
        return {
            "ok": False,
            "valid": False,
            "failed_points": [],
            "summary": f"步长 {step} mm 超过上限 {lim.max_step_mm} mm",
        }

    forbidden = _plan_has_forbidden_fields(plan)
    if forbidden:
        return {
            "ok": False,
            "valid": False,
            "failed_points": [],
            "summary": f"计划包含禁止字段: {', '.join(forbidden)}",
        }

    xs = [point.x for point in plan.points]
    ys = [point.y for point in plan.points]
    zs = [point.z for point in plan.points]
    if xs and ys:
        x_span = max(xs) - min(xs)
        y_span = max(ys) - min(ys)
        if x_span > lim.max_area_mm or y_span > lim.max_area_mm:
            return {
                "ok": False,
                "valid": False,
                "failed_points": [],
                "summary": (
                    f"区域跨度 x={x_span:.3f} y={y_span:.3f} mm "
                    f"超过上限 {lim.max_area_mm} mm"
                ),
            }

    for point in plan.points:
        result = validate_scan_point(point.x, point.y, point.z, limits=lim)
        if not result.get("ok"):
            failed_points.append(
                {
                    "index": point.index,
                    "x": point.x,
                    "y": point.y,
                    "z": point.z,
                    "reason": result.get("reason", ""),
                }
            )

    if failed_points:
        summary_parts.append(f"{len(failed_points)} 个点超出软限位")
        return {
            "ok": False,
            "valid": False,
            "failed_points": failed_points,
            "summary": "; ".join(summary_parts),
        }

    return {
        "ok": True,
        "valid": True,
        "failed_points": [],
        "summary": f"计划 {plan.plan_id} 通过安全校验（{plan.point_count()} 点）",
    }


def mark_plan_points_safe(plan: SmallAreaScanPlan, validation: dict[str, Any]) -> None:
    """根据校验结果更新各点 safe_checked 标记。"""
    safe = validation.get("valid") is True
    for point in plan.points:
        point.safe_checked = safe
