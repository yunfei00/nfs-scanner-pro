"""分析数据集 Mock — Release 021。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nfs_scanner_pro.ui import mock_data


@dataclass
class AnalysisDatasetMock:
    project_name: str = ""
    task_id: str = ""
    region_name: str = ""
    probe_name: str = ""
    frequency: str = ""
    trace: str = ""
    total_points: int = 0
    preview_points: list[dict[str, Any]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    peak_amplitude: float = -23.45
    peak_position: dict[str, float] = field(default_factory=dict)
    device_snapshot: dict[str, Any] = field(default_factory=dict)
    source_path: str = ""
    load_error: str = ""

    @classmethod
    def empty(cls, project_name: str = "") -> AnalysisDatasetMock:
        return cls(project_name=project_name or mock_data.PROJECT_NAME)

    def is_empty(self) -> bool:
        return not self.task_id

    def cursor_readout(self, index: int = 0) -> dict[str, Any]:
        if self.preview_points:
            idx = max(0, min(index, len(self.preview_points) - 1))
            point = self.preview_points[idx]
            return {
                "x": float(point.get("x", mock_data.ANALYSIS_CURSOR["x"])),
                "y": float(point.get("y", mock_data.ANALYSIS_CURSOR["y"])),
                "z": float(point.get("z", mock_data.ANALYSIS_CURSOR["z"])),
                "frequency": str(point.get("frequency", self.frequency or mock_data.FREQUENCY)),
                "amp": float(point.get("amplitude", mock_data.ANALYSIS_CURSOR["amp"])),
                "phase": float(point.get("phase", mock_data.ANALYSIS_CURSOR["phase"])),
            }
        peak = self.peak_position or {}
        return {
            "x": float(peak.get("x", mock_data.ANALYSIS_CURSOR["x"])),
            "y": float(peak.get("y", mock_data.ANALYSIS_CURSOR["y"])),
            "z": float(peak.get("z", mock_data.ANALYSIS_CURSOR["z"])),
            "frequency": self.frequency or mock_data.FREQUENCY,
            "amp": float(self.peak_amplitude or mock_data.ANALYSIS_CURSOR["amp"]),
            "phase": mock_data.ANALYSIS_CURSOR["phase"],
        }

    def as_context_text(self) -> str:
        if self.is_empty():
            return "未发现 Mock 扫描结果"
        return (
            f"{self.project_name} / {self.task_id} · "
            f"{self.total_points} 点 · 预览 {len(self.preview_points)} 点"
        )
