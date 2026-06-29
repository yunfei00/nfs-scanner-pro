"""右侧扫描参数 Dock — QDockWidget + 分组表单 Mock。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDockWidget,
    QFormLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui import mock_data


class ScanParameterDock(QDockWidget):
    DOCK_WIDTH = 340

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("扫描参数", parent)
        self.setObjectName("scanParameterDock")
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("scanParameterScroll")
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        content.setObjectName("scanParameterContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        layout.addWidget(self._build_scan_settings())
        layout.addWidget(self._build_region_settings())
        layout.addWidget(self._build_placeholder_group("displaySettingsGroup", "显示设置"))
        layout.addWidget(self._build_placeholder_group("instrumentSettingsGroup", "仪表设置"))
        layout.addWidget(self._build_placeholder_group("advancedSettingsGroup", "高级设置"))
        layout.addStretch()

        scroll.setWidget(content)
        self.setWidget(scroll)
        self.setMinimumWidth(280)
        self.resize(self.DOCK_WIDTH, self.height())

    def _build_scan_settings(self) -> QGroupBox:
        group = QGroupBox("扫描设置", self)
        group.setObjectName("scanSettingsGroup")
        group.setProperty("accordionHeader", True)
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        s = mock_data.SCAN_SETTINGS
        fields = [
            ("扫描模式", s["mode"]),
            ("驻留时间(ms)", str(s["dwell_ms"])),
            ("平均次数", str(s["averages"])),
            ("扫描速度(mm/min)", str(s["speed_mm_min"])),
            ("扫描完成后回零", "未勾选" if not s["return_home"] else "已勾选"),
            ("实时显示热力图", "勾选" if s["live_heatmap"] else "未勾选"),
        ]
        for label, val in fields:
            form.addRow(label, QLabel(val))

        if s["live_heatmap"]:
            cb = QCheckBox("实时显示热力图")
            cb.setChecked(True)
            cb.setEnabled(False)
            form.addRow("", cb)

        return group

    def _build_region_settings(self) -> QGroupBox:
        group = QGroupBox("区域设置", self)
        group.setObjectName("regionSettingsGroup")
        group.setProperty("accordionHeader", True)
        form = QFormLayout(group)
        r = mock_data.REGION_SETTINGS
        s, e, st = r["start"], r["end"], r["step"]

        def xyz(data: dict) -> str:
            return f"X={data['x']:.1f}  Y={data['y']:.1f}  Z={data['z']:.1f}"

        form.addRow("起点 X/Y/Z", QLabel(xyz(s)))
        form.addRow("终点 X/Y/Z", QLabel(xyz(e)))
        form.addRow("步长 X/Y/Z", QLabel(xyz(st)))
        form.addRow("点数", QLabel(r["points_label"]))
        form.addRow("区域面积", QLabel(r["area_mm2"]))
        form.addRow("路径长度", QLabel(r["path_length"]))
        form.addRow("预计时间", QLabel(r["estimated_time"]))
        return group

    def _build_placeholder_group(self, object_name: str, title: str) -> QGroupBox:
        group = QGroupBox(title, self)
        group.setObjectName(object_name)
        group.setProperty("accordionHeader", True)
        group.setCheckable(True)
        group.setChecked(False)
        layout = QVBoxLayout(group)
        layout.addWidget(QLabel("（Mock 占位，后续 Release 实现）"))
        return group
