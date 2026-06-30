"""报告草稿 Mock 持久化 — Release 022。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nfs_scanner_pro.app_paths import get_mock_project_dir
from nfs_scanner_pro.report.report_draft_mock import ReportDraftMock


class ReportPersistenceMock:
    DRAFT_FILENAME = "report_draft.json"

    def build_report_dir(self, project_name: str, report_id: str) -> Path:
        safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in report_id.strip())
        safe_id = safe_id or "RP-UNKNOWN"
        directory = get_mock_project_dir(project_name) / "reports" / safe_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def save_draft(self, draft: ReportDraftMock) -> tuple[bool, str]:
        try:
            report_dir = self.build_report_dir(draft.project_name, draft.report_id)
            target = report_dir / self.DRAFT_FILENAME
            target.write_text(
                json.dumps(draft.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return True, str(target)
        except OSError as exc:
            return False, str(exc)
        except (TypeError, ValueError) as exc:
            return False, str(exc)

    def load_draft(self, project_name: str, report_id: str) -> tuple[ReportDraftMock | None, str | None]:
        path = self.build_report_dir(project_name, report_id) / self.DRAFT_FILENAME
        if not path.is_file():
            return None, None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("report_draft.json 根节点必须是对象")
            return ReportDraftMock.from_dict(data), None
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
            return None, str(exc)

    def list_reports(self, project_name: str) -> list[dict[str, Any]]:
        reports_root = get_mock_project_dir(project_name) / "reports"
        if not reports_root.is_dir():
            return []
        items: list[dict[str, Any]] = []
        for report_dir in sorted(reports_root.iterdir()):
            if not report_dir.is_dir():
                continue
            draft, err = self.load_draft(project_name, report_dir.name)
            if draft is not None:
                entry = draft.to_list_item()
                entry["load_error"] = ""
                items.append(entry)
            elif err:
                items.append(
                    {
                        "id": report_dir.name,
                        "name": f"{report_dir.name}（损坏）",
                        "title": report_dir.name,
                        "time": "",
                        "meta": err,
                        "probe": "",
                        "project": project_name,
                        "region": "",
                        "frequency": "",
                        "scan_task": "",
                        "scan_time": "",
                        "summary": "",
                        "is_draft": True,
                        "load_error": err,
                    }
                )
        return items
