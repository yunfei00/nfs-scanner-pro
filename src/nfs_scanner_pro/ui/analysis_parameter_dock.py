"""分析参数面板 — QWidget 内容（由 MainWindow 单一 Dock 挂载）。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from nfs_scanner_pro.ui.widgets.analysis_control_panel import AnalysisControlPanel


class AnalysisParameterPanel(QWidget):
    """分析参数面板 — 非 QDockWidget。"""

    DOCK_WIDTH = 360

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("analysisParameterPanel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("analysisParameterScroll")
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.control_panel = AnalysisControlPanel(scroll)
        scroll.setWidget(self.control_panel)
        outer.addWidget(scroll)


AnalysisParameterDock = AnalysisParameterPanel
