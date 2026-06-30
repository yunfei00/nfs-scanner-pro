"""报告设置面板 — QWidget 内容（由 MainWindow 单一 Dock 挂载）。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class ReportSettingsPanel(QWidget):
    """报告设置面板 — 非 QDockWidget。"""

    DOCK_WIDTH = 360

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("reportSettingsPanel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("reportSettingsScroll")
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("reportSettingsContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        tpl = QGroupBox("模板", self)
        tpl.setObjectName("reportTemplateGroup")
        tf = QFormLayout(tpl)
        t_combo = QComboBox()
        t_combo.addItems(["标准 EMC 报告", "简版摘要"])
        tf.addRow("报告模板", t_combo)
        logo = QComboBox()
        logo.addItem("公司默认")
        tf.addRow("页眉 Logo", logo)
        layout.addWidget(tpl)

        export = QGroupBox("导出", self)
        export.setObjectName("reportExportGroup")
        ef = QFormLayout(export)
        quality = QComboBox()
        quality.addItems(["印刷 (300 DPI)", "屏幕 (150 DPI)"])
        ef.addRow("PDF 质量", quality)
        ef.addRow("", QCheckBox("包含热力图", checked=True))
        ef.addRow("", QCheckBox("包含设备信息", checked=True))
        ef.addRow("", QCheckBox("包含原始数据表"))
        note = QLabel("原型占位 — 不生成真实 PDF")
        note.setProperty("role", "placeholder")
        ef.addRow("", note)
        layout.addWidget(export)
        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)


ReportSettingsDock = ReportSettingsPanel
