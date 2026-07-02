"""真实扫描控制台 UI — Release 046。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui.real_scan_console_controller import RealScanConsoleController


class RealScanConsoleWidget(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("真实扫描控制台", parent)
        self.setObjectName("realScanConsoleWidget")
        self.setCheckable(True)
        self.setChecked(True)
        self._controller = RealScanConsoleController()
        self._build_ui()
        self._sync_from_model()

    @property
    def controller(self) -> RealScanConsoleController:
        return self._controller

    def refresh_hardware_mode(self) -> None:
        self._controller.refresh_hardware_mode()
        self._sync_from_model()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("当前模式："))
        self._mode_label = QLabel("Mock")
        self._mode_label.setObjectName("realScanHardwareModeLabel")
        mode_row.addWidget(self._mode_label)
        mode_row.addStretch()
        root.addLayout(mode_row)

        path_row = QHBoxLayout()
        self._plan_path = QLineEdit(self)
        self._plan_path.setObjectName("realScanPlanPathEdit")
        self._plan_path.setPlaceholderText("scan_plan.json 路径")
        path_row.addWidget(self._plan_path, stretch=1)
        self._load_btn = QPushButton("加载计划", self)
        self._load_btn.setObjectName("realScanLoadPlanButton")
        self._load_btn.clicked.connect(self._on_load_plan)
        path_row.addWidget(self._load_btn)
        self._default_btn = QPushButton("使用默认 3x3 计划", self)
        self._default_btn.setObjectName("realScanDefaultPlanButton")
        self._default_btn.clicked.connect(self._on_load_default)
        path_row.addWidget(self._default_btn)
        root.addLayout(path_row)

        self._summary_label = QLabel("计划摘要：未加载", self)
        self._summary_label.setObjectName("realScanPlanSummaryLabel")
        self._summary_label.setWordWrap(True)
        root.addWidget(self._summary_label)

        mode_pick = QHBoxLayout()
        mode_pick.addWidget(QLabel("执行模式："))
        self._exec_mode = QComboBox(self)
        self._exec_mode.setObjectName("realScanExecutionModeCombo")
        self._exec_mode.addItem("Dry Run", "dry_run")
        self._exec_mode.addItem("Fake Run", "fake_run")
        self._exec_mode.addItem("Real Run", "real_run")
        self._exec_mode.setCurrentIndex(0)
        mode_pick.addWidget(self._exec_mode)
        mode_pick.addStretch()
        root.addLayout(mode_pick)

        btn_row1 = QHBoxLayout()
        self._validate_btn = QPushButton("验证计划", self)
        self._validate_btn.setObjectName("realScanValidateButton")
        self._validate_btn.clicked.connect(self._on_validate)
        btn_row1.addWidget(self._validate_btn)
        self._dry_btn = QPushButton("执行 Dry Run", self)
        self._dry_btn.setObjectName("realScanDryRunButton")
        self._dry_btn.clicked.connect(self._on_dry_run)
        btn_row1.addWidget(self._dry_btn)
        self._fake_btn = QPushButton("执行 Fake Run", self)
        self._fake_btn.setObjectName("realScanFakeRunButton")
        self._fake_btn.clicked.connect(self._on_fake_run)
        btn_row1.addWidget(self._fake_btn)
        root.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        self._real_btn = QPushButton("执行 Real Run", self)
        self._real_btn.setObjectName("realScanRealRunButton")
        self._real_btn.clicked.connect(self._on_real_run)
        btn_row2.addWidget(self._real_btn)
        self._pause_btn = QPushButton("暂停", self)
        self._pause_btn.setObjectName("realScanPauseButton")
        self._pause_btn.clicked.connect(self._on_pause)
        btn_row2.addWidget(self._pause_btn)
        self._resume_btn = QPushButton("恢复", self)
        self._resume_btn.setObjectName("realScanResumeButton")
        self._resume_btn.clicked.connect(self._on_resume)
        btn_row2.addWidget(self._resume_btn)
        self._stop_btn = QPushButton("停止", self)
        self._stop_btn.setObjectName("realScanStopButton")
        self._stop_btn.clicked.connect(self._on_stop)
        btn_row2.addWidget(self._stop_btn)
        root.addLayout(btn_row2)

        self._safe_label = QLabel("", self)
        self._safe_label.setObjectName("realScanSafeMessageLabel")
        self._safe_label.setWordWrap(True)
        self._safe_label.setProperty("role", "warning")
        root.addWidget(self._safe_label)

        progress_form = QFormLayout()
        self._total_label = QLabel("0")
        self._index_label = QLabel("-1")
        self._completed_label = QLabel("0")
        self._failed_label = QLabel("0")
        progress_form.addRow("total_points", self._total_label)
        progress_form.addRow("current_index", self._index_label)
        progress_form.addRow("completed_points", self._completed_label)
        progress_form.addRow("failed_points", self._failed_label)
        root.addLayout(progress_form)

        self._progress = QProgressBar(self)
        self._progress.setObjectName("realScanProgressBar")
        self._progress.setRange(0, 100)
        root.addWidget(self._progress)

        self._log_view = QTextEdit(self)
        self._log_view.setObjectName("realScanLogView")
        self._log_view.setReadOnly(True)
        self._log_view.setMinimumHeight(120)
        root.addWidget(self._log_view)

        outputs_form = QFormLayout()
        self._out_json = QLineEdit(self)
        self._out_json.setReadOnly(True)
        self._out_csv = QLineEdit(self)
        self._out_csv.setReadOnly(True)
        self._out_summary = QLineEdit(self)
        self._out_summary.setReadOnly(True)
        self._out_log = QLineEdit(self)
        self._out_log.setReadOnly(True)
        outputs_form.addRow("scan_result.json", self._out_json)
        outputs_form.addRow("scan_points.csv", self._out_csv)
        outputs_form.addRow("scan_summary.json", self._out_summary)
        outputs_form.addRow("scan_log.jsonl", self._out_log)
        root.addLayout(outputs_form)

    def _sync_from_model(self) -> None:
        model = self._controller.model
        self._mode_label.setText(model.hardware_mode.capitalize())
        self._safe_label.setText(model.safe_message)
        self._real_btn.setEnabled(model.real_run_enabled)
        if model.plan_path:
            self._plan_path.setText(model.plan_path)
        summary = model.plan_summary
        if summary:
            self._summary_label.setText(
                "计划摘要："
                f"plan_id={summary.get('plan_id')} "
                f"project={summary.get('project_name')} "
                f"region={summary.get('region_name')} "
                f"points={summary.get('point_count')} "
                f"x={summary.get('x_range')} y={summary.get('y_range')} z={summary.get('z_range')} "
                f"freq={summary.get('frequency')} trace={summary.get('trace')} "
                f"dry_run={summary.get('dry_run')} safe_mode={summary.get('safe_mode')}"
            )
        progress = model.progress
        total = int(progress.get("total_points", summary.get("point_count", 0) or 0))
        completed = int(progress.get("completed_points", 0))
        failed = int(progress.get("failed_points", 0))
        current = progress.get("current_index", -1)
        self._total_label.setText(str(total))
        self._index_label.setText(str(current))
        self._completed_label.setText(str(completed))
        self._failed_label.setText(str(failed))
        if total > 0:
            self._progress.setValue(min(100, int(completed * 100 / total)))
        else:
            self._progress.setValue(0)
        self._log_view.setPlainText("\n".join(model.logs))
        paths = model.output_paths
        self._out_json.setText(paths.get("json_path", ""))
        self._out_csv.setText(paths.get("csv_path", ""))
        self._out_summary.setText(paths.get("summary_path", ""))
        self._out_log.setText(paths.get("log_path", ""))

    def _on_load_plan(self) -> None:
        path = self._plan_path.text().strip()
        if not path:
            self._controller.model.append_log("请填写 scan_plan.json 路径")
            self._sync_from_model()
            return
        self._controller.load_plan(path)
        self._sync_from_model()

    def _on_load_default(self) -> None:
        self._controller.load_default_3x3_plan()
        self._sync_from_model()

    def _on_validate(self) -> None:
        self._controller.validate_current_plan()
        self._sync_from_model()

    def _on_dry_run(self) -> None:
        self._exec_mode.setCurrentIndex(0)
        self._controller.run_dry_run()
        self._sync_from_model()

    def _on_fake_run(self) -> None:
        self._exec_mode.setCurrentIndex(1)
        self._controller.run_fake_run()
        self._sync_from_model()

    def _on_real_run(self) -> None:
        self._exec_mode.setCurrentIndex(2)
        self._controller.run_real_run()
        self._sync_from_model()

    def _on_pause(self) -> None:
        self._controller.pause()
        self._sync_from_model()

    def _on_resume(self) -> None:
        self._controller.resume()
        self._sync_from_model()

    def _on_stop(self) -> None:
        self._controller.stop()
        self._sync_from_model()
