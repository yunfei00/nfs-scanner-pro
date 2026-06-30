"""分析数据源读取 — 从 runtime/mock_projects 加载 Release 020 结果。"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from nfs_scanner_pro.app_paths import get_mock_projects_dir, get_mock_scan_dir
from nfs_scanner_pro.analysis.analysis_dataset_mock import AnalysisDatasetMock
from nfs_scanner_pro.scan.scan_result_persistence_mock import ScanResultPersistenceMock


class AnalysisDataSourceMock:
    MAX_PREVIEW_ROWS = 200

    def __init__(self) -> None:
        self._persistence = ScanResultPersistenceMock()

    def list_projects(self) -> list[str]:
        root = get_mock_projects_dir()
        if not root.is_dir():
            return []
        return sorted(p.name for p in root.iterdir() if p.is_dir())

    def list_scan_tasks(self, project_name: str) -> list[str]:
        return self._persistence.list_scan_tasks(project_name)

    def has_scan_results(self, project_name: str) -> bool:
        return bool(self.list_scan_tasks(project_name))

    def load_scan_summary(self, project_name: str, task_id: str) -> tuple[dict[str, Any] | None, str | None]:
        summary = self._persistence.load_summary(project_name, task_id)
        if summary is None:
            path = get_mock_scan_dir(project_name, task_id) / "scan_summary.json"
            if not path.is_file():
                return None, None
            return None, f"scan_summary.json 损坏或无法读取：{path}"
        return summary, None

    def load_scan_result(self, project_name: str, task_id: str) -> tuple[dict[str, Any] | None, str | None]:
        path = get_mock_scan_dir(project_name, task_id) / "scan_result.json"
        if not path.is_file():
            return None, None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("scan_result.json 根节点必须是对象")
            return data, None
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            return None, str(exc)

    def load_points_preview(
        self,
        project_name: str,
        task_id: str,
    ) -> tuple[list[dict[str, Any]], str | None]:
        path = get_mock_scan_dir(project_name, task_id) / "scan_points_preview.csv"
        if not path.is_file():
            return [], None
        try:
            rows: list[dict[str, Any]] = []
            with path.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                for index, row in enumerate(reader):
                    if index >= self.MAX_PREVIEW_ROWS:
                        break
                    rows.append(
                        {
                            "index": int(float(row.get("index", 0) or 0)),
                            "x": float(row.get("x", 0) or 0),
                            "y": float(row.get("y", 0) or 0),
                            "z": float(row.get("z", 0) or 0),
                            "frequency": row.get("frequency", ""),
                            "amplitude": float(row.get("amplitude", 0) or 0),
                            "phase": float(row.get("phase", 0) or 0),
                            "timestamp": row.get("timestamp", ""),
                        }
                    )
            return rows, None
        except (OSError, ValueError, TypeError) as exc:
            return [], str(exc)

    def build_dataset(self, project_name: str, task_id: str) -> AnalysisDatasetMock:
        scan_dir = get_mock_scan_dir(project_name, task_id)
        source_path = str(scan_dir)
        errors: list[str] = []

        summary, summary_err = self.load_scan_summary(project_name, task_id)
        if summary_err:
            errors.append(summary_err)

        result, result_err = self.load_scan_result(project_name, task_id)
        if result_err:
            errors.append(result_err)

        preview, preview_err = self.load_points_preview(project_name, task_id)
        if preview_err:
            errors.append(preview_err)

        if not summary and not result and not preview:
            return AnalysisDatasetMock.empty(project_name)

        peak = (summary or {}).get("peak_position") or {}
        if not isinstance(peak, dict):
            peak = {}
        total_points = 0
        if result:
            total_points = int(result.get("total_points", 0) or 0)
        elif summary:
            total_points = int(summary.get("total_points", 0) or 0)

        dataset = AnalysisDatasetMock(
            project_name=str((result or {}).get("project_name", project_name)),
            task_id=str((result or {}).get("task_id", task_id)),
            region_name=str((result or {}).get("region_name", "")),
            probe_name=str((result or {}).get("probe_name", "")),
            frequency=str((result or {}).get("frequency", "")),
            trace=str((result or {}).get("trace", "Trace 1")),
            total_points=total_points,
            preview_points=preview,
            summary=summary or {},
            peak_amplitude=float((summary or {}).get("peak_amplitude", -23.45)),
            peak_position={
                "x": float(peak.get("x", 45.20)),
                "y": float(peak.get("y", -28.30)),
                "z": float(peak.get("z", 5.00)),
            },
            device_snapshot=(result or {}).get("device_snapshot") or {},
            source_path=source_path,
            load_error="; ".join(errors),
        )
        return dataset

    def resolve_project_and_tasks(self, preferred_project: str) -> tuple[str, list[str]]:
        tasks = self.list_scan_tasks(preferred_project)
        if tasks:
            return preferred_project, tasks
        for project in self.list_projects():
            project_tasks = self.list_scan_tasks(project)
            if project_tasks:
                return project, project_tasks
        return preferred_project, []
