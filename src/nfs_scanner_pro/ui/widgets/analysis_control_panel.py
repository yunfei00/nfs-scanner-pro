"""分析参数 Dock 内容面板 — Release 014。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.widgets.cursor_readout_panel import CursorReadoutPanel
from nfs_scanner_pro.ui.widgets.lut_selector import LutSelector


class AnalysisControlPanel(QWidget):
    params_changed = Signal(dict)
    export_requested = Signal(str)
    cursor_lock_changed = Signal(bool)
    cursor_copy_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("analysisParameterContent")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        layout.addWidget(self._build_source_group())
        layout.addWidget(self._build_display_group())
        self._cursor_panel = CursorReadoutPanel(self)
        layout.addWidget(self._cursor_panel)
        layout.addWidget(self._build_export_group())
        layout.addWidget(self._build_advanced_group())
        layout.addStretch()

        self._cursor_panel.update_readout(mock_data.ANALYSIS_CURSOR)
        self._wire_signals()

    def _build_source_group(self) -> QGroupBox:
        group = QGroupBox("数据源", self)
        group.setObjectName("analysisSourceGroup")
        form = QFormLayout(group)
        t = mock_data.ANALYSIS_TASK

        for label, val in (
            ("ScanTask", t["scan_task"]),
            ("数据点", str(t["points"])),
            ("探头", t["probe"]),
        ):
            lbl = QLabel(val, group)
            lbl.setProperty("role", "statValue")
            form.addRow(f"{label}：", lbl)

        self._trace_combo = QComboBox(group)
        self._trace_combo.setObjectName("analysisTraceCombo")
        self._trace_combo.addItems(mock_data.ANALYSIS_TRACES)
        form.addRow("Trace 选择", self._trace_combo)

        self._freq_combo = QComboBox(group)
        self._freq_combo.setObjectName("analysisFreqCombo")
        self._freq_combo.addItems(mock_data.ANALYSIS_FREQUENCIES)
        form.addRow("频率选择", self._freq_combo)

        return group

    def _build_display_group(self) -> QGroupBox:
        group = QGroupBox("显示设置", self)
        group.setObjectName("analysisDisplayGroup")
        form = QFormLayout(group)
        t = mock_data.ANALYSIS_TASK

        self._mode_combo = QComboBox(group)
        self._mode_combo.setObjectName("analysisModeCombo")
        self._mode_combo.addItems(["幅度", "相位", "实部", "虚部"])
        self._mode_combo.setCurrentText(t["mode"])
        form.addRow("显示模式", self._mode_combo)

        self._lut_selector = LutSelector(group)
        form.addRow("LUT", self._lut_selector)

        self._vmin_edit = QLineEdit(str(t["vmin"]), group)
        self._vmin_edit.setObjectName("analysisVminEdit")
        form.addRow("vmin", self._vmin_edit)

        self._vmax_edit = QLineEdit(str(t["vmax"]), group)
        self._vmax_edit.setObjectName("analysisVmaxEdit")
        form.addRow("vmax", self._vmax_edit)

        opacity_row = QHBoxLayout()
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal, group)
        self._opacity_slider.setObjectName("analysisOpacitySlider")
        self._opacity_slider.setRange(0, 100)
        self._opacity_slider.setValue(t["opacity"])
        self._opacity_label = QLabel(f"{t['opacity']}%", group)
        self._opacity_label.setObjectName("analysisOpacityLabel")
        self._opacity_label.setMinimumWidth(40)
        opacity_row.addWidget(self._opacity_slider, stretch=1)
        opacity_row.addWidget(self._opacity_label)
        form.addRow("透明度", opacity_row)

        return group

    def _build_export_group(self) -> QGroupBox:
        group = QGroupBox("导出", self)
        group.setObjectName("analysisExportGroup")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        for obj_name, text, action in (
            ("exportHeatmapButton", "导出热力图图片", "已导出热力图图片"),
            ("exportReadoutButton", "导出当前读数", "已导出当前读数"),
            ("saveSnapshotButton", "保存分析快照", "分析快照已保存"),
        ):
            btn = QPushButton(text, group)
            btn.setObjectName(obj_name)
            btn.setProperty("variant", "secondary")
            btn.clicked.connect(lambda _=False, a=action: self.export_requested.emit(a))
            layout.addWidget(btn)

        return group

    def _build_advanced_group(self) -> QGroupBox:
        group = QGroupBox("高级", self)
        group.setObjectName("analysisAdvancedGroup")
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

    def _wire_signals(self) -> None:
        self._trace_combo.currentTextChanged.connect(lambda _: self._emit_params())
        self._freq_combo.currentTextChanged.connect(lambda _: self._emit_params())
        self._mode_combo.currentTextChanged.connect(lambda _: self._emit_params())
        self._lut_selector.value_changed.connect(lambda _: self._emit_params())
        self._vmin_edit.editingFinished.connect(self._emit_params)
        self._vmax_edit.editingFinished.connect(self._emit_params)
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)
        self._cursor_panel.lock_toggled.connect(self.cursor_lock_changed.emit)
        self._cursor_panel.copy_requested.connect(self.cursor_copy_requested.emit)

    def _on_opacity_changed(self, value: int) -> None:
        self._opacity_label.setText(f"{value}%")
        self._emit_params()

    def _emit_params(self) -> None:
        try:
            vmin = float(self._vmin_edit.text())
            vmax = float(self._vmax_edit.text())
        except ValueError:
            vmin = mock_data.ANALYSIS_TASK["vmin"]
            vmax = mock_data.ANALYSIS_TASK["vmax"]
        self.params_changed.emit(
            {
                "trace": self._trace_combo.currentText(),
                "frequency": self._freq_combo.currentText(),
                "mode": self._mode_combo.currentText(),
                "lut": self._lut_selector.currentText(),
                "vmin": vmin,
                "vmax": vmax,
                "opacity": self._opacity_slider.value(),
            }
        )

    def update_cursor_panel(self, data: dict) -> None:
        self._cursor_panel.update_readout(data)

    def set_cursor_locked(self, locked: bool) -> None:
        self._cursor_panel.set_locked(locked)
