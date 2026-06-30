"""分析参数面板 — QWidget 内容（由 MainWindow 单一 Dock 挂载）。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui.widgets.analysis_control_panel import AnalysisControlPanel


class AnalysisDataSourcePanel(QWidget):
    """ScanTask 数据源选择 — Release 021。"""

    scan_task_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("analysisDataSourcePanel")

        group = QGroupBox("数据源", self)
        group.setObjectName("analysisDataSourceGroup")
        form = QFormLayout(group)

        self._project_label = QLabel("—", group)
        self._project_label.setObjectName("analysisProjectLabel")
        self._project_label.setProperty("role", "statValue")
        form.addRow("项目：", self._project_label)

        self._task_combo = QComboBox(group)
        self._task_combo.setObjectName("analysisScanTaskCombo")
        self._task_combo.currentTextChanged.connect(self._on_task_changed)
        form.addRow("ScanTask：", self._task_combo)

        self._status_label = QLabel("未发现扫描结果", group)
        self._status_label.setObjectName("analysisDataStatusLabel")
        self._status_label.setProperty("role", "statValue")
        self._status_label.setWordWrap(True)
        form.addRow("数据状态：", self._status_label)

        self._points_label = QLabel("—", group)
        self._points_label.setProperty("role", "statValue")
        form.addRow("数据点：", self._points_label)

        self._preview_label = QLabel("—", group)
        self._preview_label.setProperty("role", "statValue")
        form.addRow("预览点：", self._preview_label)

        self._source_label = QLabel("—", group)
        self._source_label.setObjectName("analysisSourcePathLabel")
        self._source_label.setProperty("role", "statValue")
        self._source_label.setWordWrap(True)
        form.addRow("文件来源：", self._source_label)

        self._hint_label = QLabel("", group)
        self._hint_label.setObjectName("analysisDataSourceHint")
        self._hint_label.setProperty("role", "placeholder")
        self._hint_label.setWordWrap(True)
        form.addRow("", self._hint_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(group)

    def _on_task_changed(self, task_id: str) -> None:
        if task_id:
            self.scan_task_changed.emit(task_id)

    def update_view(
        self,
        *,
        project_name: str,
        task_ids: list[str],
        selected_task: str,
        dataset_loaded: bool,
        total_points: int,
        preview_points: int,
        source_path: str,
        hint: str = "",
    ) -> None:
        self._project_label.setText(project_name)
        self._task_combo.blockSignals(True)
        self._task_combo.clear()
        self._task_combo.addItems(task_ids)
        if selected_task and selected_task in task_ids:
            self._task_combo.setCurrentText(selected_task)
        self._task_combo.setEnabled(bool(task_ids))
        self._task_combo.blockSignals(False)

        if dataset_loaded:
            self._status_label.setText("已加载")
            self._points_label.setText(str(total_points or "—"))
            self._preview_label.setText(str(preview_points))
            self._source_label.setText(source_path or "—")
            self._hint_label.setText("")
        else:
            self._status_label.setText("未发现扫描结果")
            self._points_label.setText("—")
            self._preview_label.setText("—")
            self._source_label.setText(source_path or "runtime/mock_projects/...")
            self._hint_label.setText(
                hint or "未发现 Mock 扫描结果，请先在扫描页完成一次 Mock 扫描。"
            )


class AnalysisParameterPanel(QWidget):
    """分析参数面板 — 非 QDockWidget。"""

    scan_task_changed = Signal(str)

    DOCK_WIDTH = 360

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("analysisParameterPanel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.data_source_panel = AnalysisDataSourcePanel(self)
        outer.addWidget(self.data_source_panel)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("analysisParameterScroll")
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.control_panel = AnalysisControlPanel(scroll)
        scroll.setWidget(self.control_panel)
        outer.addWidget(scroll)

        legacy = self.control_panel.findChild(QGroupBox, "analysisSourceGroup")
        if legacy is not None:
            legacy.hide()

        self.data_source_panel.scan_task_changed.connect(self.scan_task_changed.emit)


AnalysisParameterDock = AnalysisParameterPanel
