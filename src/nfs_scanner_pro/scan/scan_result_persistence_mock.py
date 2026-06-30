"""扫描结果 Mock 持久化 — Release 020。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nfs_scanner_pro.app_paths import get_mock_project_dir, get_mock_scan_dir
from nfs_scanner_pro.scan.scan_path_mock import ScanPathMock
from nfs_scanner_pro.scan.scan_point import ScanPointMock
from nfs_scanner_pro.scan.scan_result_mock import ScanResultMock
from nfs_scanner_pro.scan.scan_result_serializer import (
    build_summary_dict,
    points_to_csv_content,
    result_to_json_dict,
    write_json,
)


class ScanResultPersistenceMock:
    def build_scan_dir(self, project_name: str, task_id: str) -> Path:
        return get_mock_scan_dir(project_name, task_id)

    def save_result(self, result: ScanResultMock) -> tuple[bool, str]:
        try:
            scan_dir = self.build_scan_dir(result.config.project_name, result.task_id)
            self.save_result_json(result, scan_dir)
            preview = result.preview_points or self.generate_preview_points(result.path)
            self.save_points_preview(result, scan_dir, preview_points=preview)
            self.save_summary(result, scan_dir, preview_points=preview)
            return True, str(scan_dir)
        except OSError as exc:
            return False, str(exc)
        except (TypeError, ValueError) as exc:
            return False, str(exc)

    def save_result_json(self, result: ScanResultMock, scan_dir: Path) -> Path:
        scan_dir.mkdir(parents=True, exist_ok=True)
        target = scan_dir / "scan_result.json"
        write_json(target, result_to_json_dict(result))
        return target

    def save_points_preview(
        self,
        result: ScanResultMock,
        scan_dir: Path,
        *,
        preview_points: list[ScanPointMock] | None = None,
        max_points: int = 200,
    ) -> Path:
        scan_dir.mkdir(parents=True, exist_ok=True)
        points = preview_points or self.generate_preview_points(result.path, max_points=max_points)
        target = scan_dir / "scan_points_preview.csv"
        target.write_text(points_to_csv_content(points), encoding="utf-8")
        return target

    def save_summary(
        self,
        result: ScanResultMock,
        scan_dir: Path,
        *,
        preview_points: list[ScanPointMock] | None = None,
    ) -> Path:
        scan_dir.mkdir(parents=True, exist_ok=True)
        points = preview_points or self.generate_preview_points(result.path)
        target = scan_dir / "scan_summary.json"
        write_json(target, build_summary_dict(result, points))
        return target

    def load_summary(self, project_name: str, task_id: str) -> dict[str, Any] | None:
        path = self.build_scan_dir(project_name, task_id) / "scan_summary.json"
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            return None

    def list_scan_tasks(self, project_name: str) -> list[str]:
        scans_root = get_mock_project_dir(project_name) / "scans"
        if not scans_root.is_dir():
            return []
        return sorted(p.name for p in scans_root.iterdir() if p.is_dir())

    def generate_preview_points(
        self,
        path: ScanPathMock | None,
        *,
        max_points: int = 200,
    ) -> list[ScanPointMock]:
        return self._build_preview_points(path, max_points=max_points)

    @staticmethod
    def _build_preview_points(
        path: ScanPathMock | None,
        *,
        max_points: int = 200,
    ) -> list[ScanPointMock]:
        if path is None or path.point_count() <= 0:
            return []
        total = path.point_count()
        if total <= max_points:
            indices = list(range(1, total + 1))
        else:
            step = total / max_points
            indices = sorted({min(total, int(i * step) + 1) for i in range(max_points)})
        return [path.get_point(index) for index in indices]
