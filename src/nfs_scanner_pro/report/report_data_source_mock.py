"""报告数据源 Mock — 复用 AnalysisDataSourceMock（Release 022）。"""

from __future__ import annotations

import re
from typing import Any

from nfs_scanner_pro.analysis.analysis_data_source_mock import AnalysisDataSourceMock
from nfs_scanner_pro.analysis.analysis_dataset_mock import AnalysisDatasetMock
from nfs_scanner_pro.report.report_draft_mock import ReportDraftMock


class ReportDataSourceMock:
    def __init__(self) -> None:
        self._analysis = AnalysisDataSourceMock()

    def list_projects(self) -> list[str]:
        return self._analysis.list_projects()

    def list_scan_tasks(self, project_name: str) -> list[str]:
        return self._analysis.list_scan_tasks(project_name)

    def has_report_source(self, project_name: str) -> bool:
        return self._analysis.has_scan_results(project_name)

    def load_analysis_dataset(self, project_name: str, task_id: str) -> AnalysisDatasetMock:
        return self._analysis.build_dataset(project_name, task_id)

    def build_report_context(
        self,
        project_name: str,
        task_id: str,
    ) -> dict[str, Any]:
        dataset = self.load_analysis_dataset(project_name, task_id)
        errors: list[str] = []
        if dataset.load_error:
            errors.append(dataset.load_error)
        if dataset.is_empty():
            errors.append("未发现可用扫描结果文件")
        return {
            "project_name": project_name,
            "task_id": task_id,
            "dataset": dataset,
            "default_name": self.default_report_name(
                dataset.project_name or project_name,
                dataset.region_name or "CPU_Area",
                dataset.probe_name or "Hx(100 μm)",
                dataset.frequency or "2.450 GHz",
            ),
            "errors": errors,
            "has_data": not dataset.is_empty(),
        }

    def default_report_name(
        self,
        project_name: str,
        region_name: str,
        probe_name: str,
        frequency: str,
    ) -> str:
        del project_name
        probe_short = "Hx"
        if "Hy" in probe_name:
            probe_short = "Hy"
        elif "Hx" in probe_name:
            probe_short = "Hx"
        match = re.search(r"([\d.]+)\s*GHz", frequency, re.IGNORECASE)
        if match:
            freq_short = f"{float(match.group(1)):g}GHz"
        else:
            freq_short = frequency.replace(" ", "")
        return f"{region_name}_{probe_short}_{freq_short}_报告"

    def build_virtual_report_item(
        self,
        project_name: str,
        task_id: str,
    ) -> dict[str, Any] | None:
        context = self.build_report_context(project_name, task_id)
        dataset: AnalysisDatasetMock = context["dataset"]
        if not context["has_data"]:
            return None
        draft = ReportDraftMock.from_analysis_dataset(
            dataset,
            {},
            report_name=context["default_name"],
        )
        item = draft.to_list_item()
        item["is_draft"] = False
        item["virtual"] = True
        return item

    def resolve_project_and_tasks(self, preferred_project: str) -> tuple[str, list[str]]:
        return self._analysis.resolve_project_and_tasks(preferred_project)
