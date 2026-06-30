"""报告预览数据模型 — Release 022（不生成真实 PDF）。"""

from __future__ import annotations

from dataclasses import dataclass, field

from nfs_scanner_pro.report.report_draft_mock import ReportDraftMock


@dataclass
class ReportPreviewModel:
    title: str = ""
    basic_info: dict[str, str] = field(default_factory=dict)
    heatmap_preview: bool = True
    summary: str = ""
    footer: str = "Mock 报告预览 — 未生成真实 PDF 文件"
    empty: bool = False
    empty_message: str = ""

    @classmethod
    def from_draft(cls, draft: ReportDraftMock) -> ReportPreviewModel:
        probe_label = draft.probe_name
        if probe_label in ("Hx", "Hy"):
            probe_label = f"{probe_label}(100 μm)" if probe_label == "Hx" else "Hy(100 μm)"
        peak = draft.peak_position or {}
        peak_pos = (
            f"X {float(peak.get('x', 0)):.2f} / "
            f"Y {float(peak.get('y', 0)):.2f} / "
            f"Z {float(peak.get('z', 0)):.2f} mm"
        )
        return cls(
            title=draft.preview_title(),
            basic_info={
                "报告名称": draft.report_name,
                "项目名称": draft.project_name,
                "区域名称": draft.region_name,
                "ScanTask": draft.scan_task_id,
                "探头": probe_label,
                "扫描时间": draft.created_at,
                "频率": draft.frequency,
                "峰值幅度": f"{draft.peak_amplitude:.2f} dBm",
                "峰值位置": peak_pos,
            },
            heatmap_preview=draft.include_heatmap,
            summary=draft.preview_summary(),
            footer="Mock 报告预览 — 未生成真实 PDF 文件",
        )

    @classmethod
    def from_list_item(cls, item: dict) -> ReportPreviewModel:
        draft = ReportDraftMock.from_dict(
            {
                "report_id": item.get("id", ""),
                "report_name": item.get("name", ""),
                "project_name": item.get("project", ""),
                "region_name": item.get("region", ""),
                "scan_task_id": item.get("scan_task", ""),
                "probe_name": item.get("probe", "Hx"),
                "frequency": item.get("frequency", ""),
                "created_at": item.get("scan_time", item.get("time", "")),
                "summary": item.get("summary", ""),
                "peak_amplitude": item.get("peak_amplitude", -23.45),
                "peak_position": item.get("peak_position") or {},
            }
        )
        return cls.from_draft(draft)

    @classmethod
    def empty(cls, message: str) -> ReportPreviewModel:
        return cls(
            title="报告预览",
            empty=True,
            empty_message=message,
            heatmap_preview=False,
            summary="",
            footer="",
        )
