"""报告草稿 Mock — Release 022。"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from nfs_scanner_pro.analysis.analysis_dataset_mock import AnalysisDatasetMock


@dataclass
class ReportDraftMock:
    report_id: str = ""
    report_name: str = ""
    project_name: str = ""
    region_name: str = ""
    scan_task_id: str = ""
    probe_name: str = ""
    frequency: str = ""
    created_at: str = ""
    template: str = "标准 EMC 报告"
    logo: str = "公司默认"
    pdf_quality: str = "印刷（300 DPI）"
    include_heatmap: bool = True
    include_device_info: bool = True
    include_scan_params: bool = True
    include_raw_data: bool = False
    include_summary: bool = True
    summary: str = ""
    peak_amplitude: float = -23.45
    peak_position: dict[str, float] = field(default_factory=dict)
    source_path: str = ""

    @classmethod
    def from_analysis_dataset(
        cls,
        dataset: AnalysisDatasetMock,
        settings: dict[str, Any],
        *,
        report_name: str | None = None,
        created_at: str | None = None,
    ) -> ReportDraftMock:
        from nfs_scanner_pro.analysis.analysis_data_source_mock import AnalysisDataSourceMock
        from nfs_scanner_pro.report.report_data_source_mock import ReportDataSourceMock

        ds = ReportDataSourceMock()
        name = report_name or ds.default_report_name(
            dataset.project_name,
            dataset.region_name or "CPU_Area",
            dataset.probe_name or "Hx(100 μm)",
            dataset.frequency or "2.450 GHz",
        )
        peak = dataset.peak_position or {}
        finished = ""
        result, _ = AnalysisDataSourceMock().load_scan_result(
            dataset.project_name,
            dataset.task_id,
        )
        if result:
            finished = str(result.get("finished_at", "") or "")
        if not finished and dataset.summary:
            finished = str(dataset.summary.get("finished_at", "") or "")
        created = created_at or finished or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return cls(
            report_id=f"RP-{uuid.uuid4().hex[:8].upper()}",
            report_name=name,
            project_name=dataset.project_name,
            region_name=dataset.region_name or "CPU_Area",
            scan_task_id=dataset.task_id,
            probe_name=dataset.probe_name or "Hx(100 μm)",
            frequency=dataset.frequency or "2.450 GHz",
            created_at=created,
            template=str(settings.get("template", "标准 EMC 报告")),
            logo=str(settings.get("logo", "公司默认")),
            pdf_quality=str(settings.get("pdf_quality", "印刷（300 DPI）")),
            include_heatmap=bool(settings.get("include_heatmap", True)),
            include_device_info=bool(settings.get("include_device_info", True)),
            include_scan_params=bool(settings.get("include_scan_params", True)),
            include_raw_data=bool(settings.get("include_raw_data", False)),
            include_summary=bool(settings.get("include_summary", True)),
            summary=_build_summary(dataset),
            peak_amplitude=float(dataset.peak_amplitude),
            peak_position={
                "x": float(peak.get("x", 0.0)),
                "y": float(peak.get("y", 0.0)),
                "z": float(peak.get("z", 0.0)),
            },
            source_path=dataset.source_path,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReportDraftMock:
        peak = data.get("peak_position") or {}
        if not isinstance(peak, dict):
            peak = {}
        return cls(
            report_id=str(data.get("report_id", "")),
            report_name=str(data.get("report_name", "")),
            project_name=str(data.get("project_name", "")),
            region_name=str(data.get("region_name", "")),
            scan_task_id=str(data.get("scan_task_id", "")),
            probe_name=str(data.get("probe_name", "")),
            frequency=str(data.get("frequency", "")),
            created_at=str(data.get("created_at", "")),
            template=str(data.get("template", "标准 EMC 报告")),
            logo=str(data.get("logo", "公司默认")),
            pdf_quality=str(data.get("pdf_quality", "印刷（300 DPI）")),
            include_heatmap=bool(data.get("include_heatmap", True)),
            include_device_info=bool(data.get("include_device_info", True)),
            include_scan_params=bool(data.get("include_scan_params", True)),
            include_raw_data=bool(data.get("include_raw_data", False)),
            include_summary=bool(data.get("include_summary", True)),
            summary=str(data.get("summary", "")),
            peak_amplitude=float(data.get("peak_amplitude", -23.45)),
            peak_position={
                "x": float(peak.get("x", 0.0)),
                "y": float(peak.get("y", 0.0)),
                "z": float(peak.get("z", 0.0)),
            },
            source_path=str(data.get("source_path", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def preview_title(self) -> str:
        return f"{self.region_name} 近场扫描报告"

    def preview_summary(self) -> str:
        if self.include_summary and self.summary:
            return self.summary
        return "（未包含结论摘要）"

    def to_list_item(self) -> dict[str, Any]:
        probe_short = "Hx"
        if "Hy" in self.probe_name:
            probe_short = "Hy"
        elif "Hx" in self.probe_name:
            probe_short = "Hx"
        time_label = self.created_at[:16] if len(self.created_at) >= 16 else self.created_at
        return {
            "id": self.report_id,
            "name": self.report_name,
            "title": self.report_name,
            "time": time_label,
            "meta": f"{time_label} · {probe_short}",
            "probe": probe_short,
            "project": self.project_name,
            "region": self.region_name,
            "frequency": self.frequency,
            "scan_task": self.scan_task_id,
            "scan_time": self.created_at,
            "peak_amplitude": self.peak_amplitude,
            "peak_position": self.peak_position,
            "summary": self.summary,
            "is_draft": True,
        }


def _build_summary(dataset: AnalysisDatasetMock) -> str:
    region = dataset.region_name or "CPU 区域"
    freq = dataset.frequency or "2.450 GHz"
    amp = dataset.peak_amplitude
    pos = dataset.peak_position or {}
    x = float(pos.get("x", 45.20))
    y = float(pos.get("y", -28.30))
    return (
        f"{region} 在 {freq} 出现局部辐射峰值（{amp:.2f} dBm），"
        f"位于 X {x:.2f} / Y {y:.2f} mm 处。"
        "建议进一步 Hx / Hy 对比分析。"
    )
