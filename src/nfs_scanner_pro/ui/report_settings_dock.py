"""报告设置面板 — QWidget 内容（由 MainWindow 单一 Dock 挂载）。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui import mock_data


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

        layout.addWidget(self._build_template_group())
        layout.addWidget(self._build_export_group())
        layout.addWidget(self._build_content_group())
        layout.addWidget(self._build_advanced_group())
        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _build_template_group(self) -> QGroupBox:
        s = mock_data.REPORT_SETTINGS
        group = QGroupBox("模板", self)
        group.setObjectName("reportTemplateGroup")
        form = QFormLayout(group)

        self._template_combo = QComboBox(group)
        self._template_combo.addItems(
            ["标准 EMC 报告", "快速扫描摘要", "客户交付版"]
        )
        self._template_combo.setCurrentText(s["template"])
        form.addRow("报告模板", self._template_combo)

        self._logo_combo = QComboBox(group)
        self._logo_combo.addItems(["公司默认", "无 Logo", "自定义占位"])
        self._logo_combo.setCurrentText(s["logo"])
        form.addRow("页眉 Logo", self._logo_combo)
        return group

    def _build_export_group(self) -> QGroupBox:
        s = mock_data.REPORT_SETTINGS
        group = QGroupBox("导出", self)
        group.setObjectName("reportExportGroup")
        form = QFormLayout(group)

        self._quality_combo = QComboBox(group)
        self._quality_combo.addItems(["屏幕预览", "标准", "印刷（300 DPI）"])
        self._quality_combo.setCurrentText(s["pdf_quality"])
        form.addRow("PDF 质量", self._quality_combo)

        self._format_combo = QComboBox(group)
        self._format_combo.addItems(s["formats"])
        form.addRow("导出格式", self._format_combo)
        return group

    def _build_content_group(self) -> QGroupBox:
        s = mock_data.REPORT_SETTINGS
        group = QGroupBox("内容", self)
        group.setObjectName("reportContentGroup")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        self._cb_heatmap = QCheckBox("包含热力图", group)
        self._cb_heatmap.setChecked(s["include_heatmap"])
        self._cb_device = QCheckBox("包含设备信息", group)
        self._cb_device.setChecked(s["include_device_info"])
        self._cb_scan = QCheckBox("包含扫描参数", group)
        self._cb_scan.setChecked(s["include_scan_params"])
        self._cb_raw = QCheckBox("包含原始数据表", group)
        self._cb_raw.setChecked(s["include_raw_data"])
        self._cb_summary = QCheckBox("包含结论摘要", group)
        self._cb_summary.setChecked(s["include_summary"])

        for cb in (
            self._cb_heatmap,
            self._cb_device,
            self._cb_scan,
            self._cb_raw,
            self._cb_summary,
        ):
            layout.addWidget(cb)
        return group

    def _build_advanced_group(self) -> QGroupBox:
        from PySide6.QtWidgets import QLabel

        group = QGroupBox("高级", self)
        group.setObjectName("reportAdvancedGroup")
        group.setCheckable(True)
        group.setChecked(False)
        layout = QVBoxLayout(group)
        hint = QLabel("折叠 — 后续 Release 展开", group)
        hint.setProperty("role", "placeholder")
        layout.addWidget(hint)

        def sync_collapsed(checked: bool) -> None:
            hint.setVisible(checked)
            group.setMaximumHeight(16777215 if checked else 44)

        group.toggled.connect(sync_collapsed)
        sync_collapsed(False)
        return group


ReportSettingsDock = ReportSettingsPanel
