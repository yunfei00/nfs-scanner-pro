"""真实扫描结果写入 — Release 044。"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nfs_scanner_pro.app_paths import get_runtime_dir

CSV_FIELDS = (
    "index",
    "x",
    "y",
    "z",
    "frequency_hz",
    "amplitude_dbm",
    "unit",
    "motion_state",
    "sample_ok",
    "error",
    "timestamp_iso",
)


def _run_dir(task_id: str) -> Path:
    return get_runtime_dir() / "real_scan_runs" / task_id


def save_scan_result(
    task_id: str,
    *,
    plan_id: str,
    points: list[dict[str, Any]],
    summary: dict[str, Any],
    logs: list[dict[str, Any]] | None = None,
) -> dict[str, Path]:
    directory = _run_dir(task_id)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "scan_result.json"
    csv_path = directory / "scan_points.csv"
    summary_path = directory / "scan_summary.json"
    log_path = directory / "scan_log.jsonl"

    payload = {
        "task_id": task_id,
        "plan_id": plan_id,
        "point_count": len(points),
        "points": points,
        "summary": summary,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in points:
            writer.writerow({key: row.get(key, "") for key in CSV_FIELDS})

    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with log_path.open("w", encoding="utf-8") as handle:
        for entry in logs or []:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {
        "json_path": json_path,
        "csv_path": csv_path,
        "summary_path": summary_path,
        "log_path": log_path,
    }


def build_summary(
    *,
    task_id: str,
    plan_id: str,
    mode: str,
    total_points: int,
    completed_points: int,
    failed_points: int,
    state: str,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "plan_id": plan_id,
        "mode": mode,
        "total_points": total_points,
        "completed_points": completed_points,
        "failed_points": failed_points,
        "state": state,
        "dry_run": mode == "dry_run",
        "fake_run": mode == "fake_run",
        "real_run": mode == "real_run",
        "motion_command_executed_any": mode == "real_run",
        "sweep_started_any": False,
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
