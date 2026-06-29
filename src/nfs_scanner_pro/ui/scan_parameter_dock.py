"""右侧扫描参数 Dock — QDockWidget + 分组表单 Mock。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui import mock_data


class ScanParameterDock(QDockWidget):
    DOCK_WIDTH = 360

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
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("scanParameterContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        layout.addWidget(self._build_scan_settings())
        layout.addWidget(self._build_region_settings())
        layout.addWidget(self._build_placeholder_group("displaySettingsGroup", "显示设置"))
        layout.addWidget(self._build_placeholder_group("instrumentSettingsGroup", "仪表设置"))
        layout.addWidget(self._build_placeholder_group("advancedSettingsGroup", "高级设置"))
        layout.addStretch()

        scroll.setWidget(content)
        self.setWidget(scroll)
        self.setMinimumWidth(300)
        self.resize(self.DOCK_WIDTH, self.height())

    @staticmethod
    def _xyz_text(data: dict) -> str:
        return f"{data['x']:.2f} / {data['y']:.2f} / {data['z']:.2f}"

    def _build_scan_settings(self) -> QGroupBox:
        group = QGroupBox("扫描设置", self)
        group.setObjectName("scanSettingsGroup")
        group.setProperty("accordionHeader", True)
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setSpacing(8)

        s = mock_data.SCAN_SETTINGS

        mode = QComboBox(group)
        mode.addItem(s["mode"])
        mode.setEnabled(False)
        form.addRow("扫描模式", mode)

        for label, val in (
            ("驻留时间 (ms)", str(s["dwell_ms"])),
            ("平均次数", str(s["averages"])),
            ("扫描速度 (mm/min)", str(s["speed_mm_min"])),
        ):
            field = QLineEdit(val, group)
            field.setReadOnly(True)
            form.addRow(label, field)

        return_home = QCheckBox("扫描完成后回零", group)
        return_home.setChecked(s["return_home"])
        return_home.setEnabled(False)
        form.addRow("", return_home)

        live_heatmap = QCheckBox("实时显示热力图", group)
        live_heatmap.setChecked(s["live_heatmap"])
        live_heatmap.setEnabled(False)
        form.addRow("", live_heatmap)

        return group

    def _build_region_settings(self) -> QGroupBox:
        group = QGroupBox("区域设置", self)
        group.setObjectName("regionSettingsGroup")
        group.setProperty("accordionHeader", True)
        form = QFormLayout(group)
        form.setSpacing(8)
        r = mock_data.REGION_SETTINGS

        for label, key in (
            ("起点 X / Y / Z (mm)", "start"),
            ("终点 X / Y / Z (mm)", "end"),
            ("步长 X / Y / Z (mm)", "step"),
        ):
            field = QLineEdit(self._xyz_text(r[key]), group)
            field.setReadOnly(True)
            form.addRow(label, field)

        stats = QGridLayout()
        stats.setSpacing(6)
        stat_items = [
            ("点数", r["points_label"]),
            ("区域面积", r["area_mm2"]),
            ("路径长度", r["path_length"]),
            ("预计时间", r["estimated_time"]),
        ]
        for row, (k, v) in enumerate(stat_items):
            k_lbl = QLabel(k, group)
            k_lbl.setProperty("role", "statKey")
            v_lbl = QLabel(v, group)
            v_lbl.setProperty("role", "statValue")
            stats.addWidget(k_lbl, row, 0)
            stats.addWidget(v_lbl, row, 1)
        form.addRow("", stats)

        return group

    def _build_placeholder_group(self, object_name: str, title: str) -> QGroupBox:
        group = QGroupBox(title, self)
        group.setObjectName(object_name)
        group.setProperty("accordionHeader", True)
        group.setCheckable(True)
        group.setChecked(False)
        layout = QVBoxLayout(group)
        hint = QLabel("折叠 — 后续 Release 展开", group)
        hint.setProperty("role", "placeholder")
        layout.addWidget(hint)
        return group
