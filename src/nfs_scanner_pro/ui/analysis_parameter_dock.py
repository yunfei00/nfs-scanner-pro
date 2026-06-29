"""分析参数 Dock。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.scan_parameter_dock import apply_dock_width_policy
from nfs_scanner_pro.ui.widgets.form_widgets import stat_grid


class AnalysisParameterDock(QDockWidget):
    DOCK_WIDTH = 360

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("分析参数", parent)
        self.setObjectName("analysisParameterDock")
        apply_dock_width_policy(self)
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("analysisParameterScroll")
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("analysisParameterContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        src = QGroupBox("数据源", self)
        src.setObjectName("analysisSourceGroup")
        sf = QFormLayout(src)
        trace = QComboBox()
        trace.addItems(["Trace 1", "Trace 2"])
        sf.addRow("Trace 选择", trace)
        freq = QComboBox()
        freq.addItem(mock_data.FREQUENCY)
        sf.addRow("频率选择", freq)
        layout.addWidget(src)

        display = QGroupBox("显示", self)
        display.setObjectName("analysisDisplayGroup")
        df = QFormLayout(display)
        mode = QComboBox()
        mode.addItems(["幅度", "相位", "实部", "虚部"])
        df.addRow("显示模式", mode)
        lut = QComboBox()
        lut.addItems(["Jet", "Viridis", "Hot"])
        df.addRow("LUT 选择", lut)
        df.addRow("vmin (dBm)", QLineEdit("-90"))
        df.addRow("vmax (dBm)", QLineEdit("-10"))
        df.addRow("透明度", QLineEdit("72 %"))
        layout.addWidget(display)

        cursor = QGroupBox("光标", self)
        cursor.setObjectName("analysisCursorGroup")
        cf = QFormLayout(cursor)
        pos = mock_data.POSITION
        cf.addRow("", stat_grid(self, [
            ("X", f"{pos['x']:.2f} mm"),
            ("Y", f"{pos['y']:.2f} mm"),
            ("幅度", f"{pos['amp']:.2f} dBm"),
            ("相位", "112.3°"),
        ]))
        layout.addWidget(cursor)
        layout.addStretch()

        scroll.setWidget(content)
        self.setWidget(scroll)
