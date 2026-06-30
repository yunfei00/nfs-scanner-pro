"""右侧扫描参数面板 — QWidget 内容（由 MainWindow 单一 Dock 挂载）。"""

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
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui import mock_data

DOCK_MIN_WIDTH = 340
DOCK_MAX_WIDTH = 420
DOCK_DEFAULT_WIDTH = 360


def apply_dock_width_policy(dock: QDockWidget) -> None:
    dock.setMinimumWidth(DOCK_MIN_WIDTH)
    dock.setMaximumWidth(DOCK_MAX_WIDTH)
    dock.setBaseSize(DOCK_DEFAULT_WIDTH, 0)
    dock.resize(DOCK_DEFAULT_WIDTH, dock.height())


def _configure_form_field(field: QLineEdit | QComboBox) -> None:
    field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    field.setMinimumWidth(0)


class ScanParameterPanel(QWidget):
    """扫描参数面板 — 非 QDockWidget，仅供 right_dock.setWidget 使用。"""

    DOCK_WIDTH = DOCK_DEFAULT_WIDTH

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("scanParameterPanel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("scanParameterScroll")
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("scanParameterContent")
        content.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._lockable_fields: list[QLineEdit | QComboBox | QCheckBox | QGroupBox] = []

        layout.addWidget(self._build_scan_settings())
        layout.addWidget(self._build_region_settings())
        layout.addWidget(self._build_placeholder_group("displaySettingsGroup", "显示设置"))
        layout.addWidget(self._build_placeholder_group("instrumentSettingsGroup", "仪表设置"))
        layout.addWidget(self._build_placeholder_group("advancedSettingsGroup", "高级设置"))

        scroll.setWidget(content)
        outer.addWidget(scroll)
        self.set_fields_locked(False)

    @staticmethod
    def _configure_form(form: QFormLayout) -> None:
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        form.setSpacing(6)
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(6)

    @staticmethod
    def _xyz_text(data: dict) -> str:
        return f"{data['x']:.2f} / {data['y']:.2f} / {data['z']:.2f}"

    def _build_scan_settings(self) -> QGroupBox:
        group = QGroupBox("扫描设置", self)
        group.setObjectName("scanSettingsGroup")
        group.setProperty("accordionHeader", True)
        form = QFormLayout(group)
        self._configure_form(form)

        s = mock_data.SCAN_SETTINGS

        mode = QComboBox(group)
        mode.addItem(s["mode"])
        _configure_form_field(mode)
        form.addRow("扫描模式", mode)
        self._lockable_fields.append(mode)

        for label, val in (
            ("驻留时间 (ms)", str(s["dwell_ms"])),
            ("平均次数", str(s["averages"])),
            ("扫描速度 (mm/min)", str(s["speed_mm_min"])),
        ):
            field = QLineEdit(val, group)
            _configure_form_field(field)
            form.addRow(label, field)
            self._lockable_fields.append(field)

        return_home = QCheckBox("扫描完成后回零", group)
        return_home.setChecked(s["return_home"])
        form.addRow("", return_home)
        self._lockable_fields.append(return_home)

        live_heatmap = QCheckBox("实时显示热力图", group)
        live_heatmap.setChecked(s["live_heatmap"])
        form.addRow("", live_heatmap)
        self._lockable_fields.append(live_heatmap)

        return group

    def _build_region_settings(self) -> QGroupBox:
        group = QGroupBox("区域设置", self)
        group.setObjectName("regionSettingsGroup")
        group.setProperty("accordionHeader", True)
        form = QFormLayout(group)
        self._configure_form(form)
        r = mock_data.REGION_SETTINGS

        for label, key in (
            ("起点 X / Y / Z (mm)", "start"),
            ("终点 X / Y / Z (mm)", "end"),
            ("步长 X / Y / Z (mm)", "step"),
        ):
            field = QLineEdit(self._xyz_text(r[key]), group)
            _configure_form_field(field)
            form.addRow(label, field)
            self._lockable_fields.append(field)

        stats = QGridLayout()
        stats.setHorizontalSpacing(8)
        stats.setVerticalSpacing(4)
        stats.setColumnStretch(1, 1)
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
            v_lbl.setWordWrap(True)
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

        def sync_collapsed(checked: bool) -> None:
            hint.setVisible(checked)
            group.setMaximumHeight(16777215 if checked else 44)
            group.updateGeometry()

        group.toggled.connect(sync_collapsed)
        sync_collapsed(False)
        self._lockable_fields.append(group)
        return group

    def set_fields_locked(self, locked: bool) -> None:
        """扫描中锁定参数；完成/停止后恢复可编辑。"""
        for field in self._lockable_fields:
            if isinstance(field, QLineEdit):
                field.setReadOnly(locked)
                field.setEnabled(not locked)
                field.setProperty("scanLocked", locked)
            elif isinstance(field, (QComboBox, QCheckBox, QGroupBox)):
                field.setEnabled(not locked)
                field.setProperty("scanLocked", locked)
            field.style().unpolish(field)
            field.style().polish(field)


# 兼容旧引用名
ScanParameterDock = ScanParameterPanel
