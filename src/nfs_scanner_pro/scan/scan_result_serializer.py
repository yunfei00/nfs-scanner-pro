"""扫描结果序列化 — Release 020。"""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from nfs_scanner_pro.scan.scan_point import ScanPointMock
from nfs_scanner_pro.scan.scan_result_mock import ScanResultMock


def result_to_json_dict(result: ScanResultMock) -> dict[str, Any]:
    cfg = result.config
    return {
        "task_id": result.task_id,
        "project_name": cfg.project_name,
        "region_name": cfg.region_name,
        "probe_name": cfg.probe_name,
        "frequency": cfg.frequency,
        "trace": cfg.trace,
        "status": result.status,
        "total_points": cfg.total_points,
        "started_at": result.started_at,
        "finished_at": result.finished_at,
        "device_snapshot": result.device_snapshot,
        "result_type": "mock",
    }


def point_to_row(point: ScanPointMock) -> dict[str, Any]:
    return {
        "index": point.index,
        "x": point.x,
        "y": point.y,
        "z": point.z,
        "frequency": point.frequency,
        "amplitude": point.amplitude,
        "phase": point.phase,
        "timestamp": point.timestamp,
    }


def points_to_csv_content(points: list[ScanPointMock]) -> str:
    buffer = io.StringIO()
    fieldnames = ["index", "x", "y", "z", "frequency", "amplitude", "phase", "timestamp"]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for point in points:
        writer.writerow(point_to_row(point))
    return buffer.getvalue()


def build_summary_dict(
    result: ScanResultMock,
    preview_points: list[ScanPointMock],
) -> dict[str, Any]:
    peak_amp = -23.45
    peak_x, peak_y, peak_z = 45.20, -28.30, 5.00
    if preview_points:
        peak_point = max(preview_points, key=lambda p: p.amplitude)
        peak_amp = round(peak_point.amplitude, 2)
        peak_x, peak_y, peak_z = peak_point.x, peak_point.y, peak_point.z
    return {
        "task_id": result.task_id,
        "total_points": result.config.total_points,
        "saved_preview_points": len(preview_points),
        "peak_amplitude": peak_amp,
        "peak_position": {"x": peak_x, "y": peak_y, "z": peak_z},
        "mock": True,
    }


def write_json(path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
