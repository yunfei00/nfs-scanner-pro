"""手动扫描会话持久化 — Release 043。"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from nfs_scanner_pro.app_paths import get_runtime_dir
from nfs_scanner_pro.scan.manual_scan_session import (
    ManualScanPointStatus,
    ManualScanSession,
    session_from_dict,
)

POINTS_CSV_FIELDS = (
    "index",
    "row",
    "col",
    "planned_x",
    "planned_y",
    "planned_z",
    "status",
    "actual_x",
    "actual_y",
    "actual_z",
    "position_error_mm",
    "frequency_hz",
    "amplitude_dbm",
    "sample_id",
    "sampled_at",
    "message",
)

SAMPLES_CSV_FIELDS = (
    "session_id",
    "plan_id",
    "sample_id",
    "point_index",
    "row",
    "col",
    "planned_x",
    "planned_y",
    "planned_z",
    "actual_x",
    "actual_y",
    "actual_z",
    "position_error_mm",
    "frequency_hz",
    "frequency_ghz",
    "amplitude_dbm",
    "unit",
    "safe_mode",
    "motion_command_executed",
    "sweep_started",
    "sampled_at",
)


def _sessions_base_dir() -> Path:
    return get_runtime_dir() / "manual_scan_sessions"


def _session_dir(session_id: str) -> Path:
    return _sessions_base_dir() / session_id


def build_manual_summary(session: ManualScanSession) -> dict[str, Any]:
    return {
        "session_id": session.session_id,
        "plan_id": session.plan_id,
        "point_count": session.point_count(),
        "sampled_count": session.sampled_count(),
        "pending_count": session.pending_count(),
        "failed_count": session.failed_count(),
        "completion_ratio": session.completion_ratio(),
        "safe_mode": session.safe_mode,
        "motion_command_executed_any": False,
        "sweep_started_any": False,
    }


def _point_row(point: ManualScanPointStatus) -> dict[str, Any]:
    return {
        "index": point.index,
        "row": point.row,
        "col": point.col,
        "planned_x": point.planned_x,
        "planned_y": point.planned_y,
        "planned_z": point.planned_z,
        "status": point.status,
        "actual_x": point.actual_x if point.actual_x is not None else "",
        "actual_y": point.actual_y if point.actual_y is not None else "",
        "actual_z": point.actual_z if point.actual_z is not None else "",
        "position_error_mm": point.position_error_mm if point.position_error_mm is not None else "",
        "frequency_hz": point.frequency_hz if point.frequency_hz is not None else "",
        "amplitude_dbm": point.amplitude_dbm if point.amplitude_dbm is not None else "",
        "sample_id": point.sample_id,
        "sampled_at": point.sampled_at,
        "message": point.message,
    }


def _write_points_csv(path: Path, session: ManualScanSession) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=POINTS_CSV_FIELDS)
        writer.writeheader()
        for point in session.points:
            writer.writerow(_point_row(point))


def _read_samples_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_samples_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SAMPLES_CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def save_manual_scan_session(session: ManualScanSession) -> dict[str, Path]:
    directory = _session_dir(session.session_id)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "manual_scan_session.json"
    points_path = directory / "manual_scan_points.csv"
    summary_path = directory / "manual_scan_summary.json"

    json_path.write_text(
        json.dumps(session.as_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _write_points_csv(points_path, session)
    summary_path.write_text(
        json.dumps(build_manual_summary(session), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {
        "session_json": json_path,
        "points_csv": points_path,
        "summary_json": summary_path,
    }


def load_manual_scan_session(path: str | Path) -> ManualScanSession:
    json_path = Path(path)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return session_from_dict(data)


def append_manual_sample(
    session: ManualScanSession,
    point_status: ManualScanPointStatus,
    sample_record: dict[str, Any],
) -> Path:
    directory = _session_dir(session.session_id)
    directory.mkdir(parents=True, exist_ok=True)
    samples_path = directory / "manual_scan_samples.csv"
    spectrum = sample_record.get("spectrum", {})
    row = {
        "session_id": session.session_id,
        "plan_id": session.plan_id,
        "sample_id": sample_record.get("sample_id", point_status.sample_id),
        "point_index": point_status.index,
        "row": point_status.row,
        "col": point_status.col,
        "planned_x": point_status.planned_x,
        "planned_y": point_status.planned_y,
        "planned_z": point_status.planned_z,
        "actual_x": point_status.actual_x if point_status.actual_x is not None else "",
        "actual_y": point_status.actual_y if point_status.actual_y is not None else "",
        "actual_z": point_status.actual_z if point_status.actual_z is not None else "",
        "position_error_mm": point_status.position_error_mm if point_status.position_error_mm is not None else "",
        "frequency_hz": spectrum.get("frequency_hz", point_status.frequency_hz),
        "frequency_ghz": spectrum.get("frequency_ghz", ""),
        "amplitude_dbm": spectrum.get("amplitude_dbm", point_status.amplitude_dbm),
        "unit": spectrum.get("unit", "dBm"),
        "safe_mode": sample_record.get("safe_mode", True),
        "motion_command_executed": sample_record.get("motion_command_executed", False),
        "sweep_started": sample_record.get("sweep_started", False),
        "sampled_at": point_status.sampled_at,
    }
    existing = _read_samples_csv(samples_path)
    existing.append({key: str(row.get(key, "")) for key in SAMPLES_CSV_FIELDS})
    _write_samples_csv(samples_path, existing)
    return samples_path


def save_manual_summary(session: ManualScanSession) -> Path:
    directory = _session_dir(session.session_id)
    directory.mkdir(parents=True, exist_ok=True)
    summary_path = directory / "manual_scan_summary.json"
    summary_path.write_text(
        json.dumps(build_manual_summary(session), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary_path


def list_manual_scan_sessions() -> list[str]:
    base = _sessions_base_dir()
    if not base.is_dir():
        return []
    return sorted(
        child.name
        for child in base.iterdir()
        if child.is_dir() and (child / "manual_scan_session.json").is_file()
    )
