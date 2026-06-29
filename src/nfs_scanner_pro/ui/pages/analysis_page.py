"""分析页 — PCB + 热力图。"""

from __future__ import annotations

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.scan_canvas_view import PcbCanvasWidget


class AnalysisPage(PcbCanvasWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(
            object_name="analysisPage",
            breadcrumb=mock_data.BREADCRUMB_ANALYSIS,
            show_minimap=False,
            show_handles=False,
            overlay_mode="cursor",
            parent=parent,
        )
