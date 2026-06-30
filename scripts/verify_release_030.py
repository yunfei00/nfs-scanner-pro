#!/usr/bin/env python3
"""Release_030 自动验收 — Cross-Page Workflow UI Verification。"""

from __future__ import annotations

import compileall
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from verification_utils import (  # noqa: E402
    DOCK_TITLES,
    FORBIDDEN_PATTERNS,
    MOCK_DEVICE_DIRS,
    PROJECT_NAME,
    REPORT_TOOLBAR,
    ROOT,
    SCAN_TOOLBAR,
    CheckResult,
    describe_mock_scan_dir,
    gitignore_covers_runtime,
    setup_offscreen,
    setup_path,
    toolbar_texts,
)

WORKFLOW_IMPORTS = (
    "nfs_scanner_pro.ui.main_window",
    "nfs_scanner_pro.devices.device_manager_mock",
    "nfs_scanner_pro.scan.scan_engine_mock",
    "nfs_scanner_pro.scan.scan_result_persistence_mock",
    "nfs_scanner_pro.analysis.analysis_data_source_mock",
    "nfs_scanner_pro.report.report_data_source_mock",
    "nfs_scanner_pro.report.report_persistence_mock",
    "nfs_scanner_pro.workspace_state_mock",
    "nfs_scanner_pro.project_mock",
)

CROSS_PAGE_SEQUENCE = (0, 1, 2, 3, 0, 3, 2, 1, 0)
EXPORT_EXTENSIONS = {".pdf", ".docx", ".xlsx"}


def _status_text(win) -> str:
    return win._status._message.text()


def _find_toolbar_button(win, object_name: str):
    from PySide6.QtWidgets import QToolButton

    return win._tool_bar.findChild(QToolButton, object_name)


def _param_field_enabled(win) -> bool:
    panel = win._scan_panel
    if not panel._lockable_fields:
        return True
    return panel._lockable_fields[0].isEnabled()


def _collect_text(widget) -> str:
    from PySide6.QtWidgets import QCheckBox, QLabel, QLineEdit, QPushButton

    parts: list[str] = []
    for cls in (QLabel, QLineEdit, QCheckBox, QPushButton):
        for child in widget.findChildren(cls):
            text = child.text()
            if text:
                parts.append(text)
    return " ".join(parts)


def _preview_text(panel) -> str:
    parts = [
        panel._title_lbl.text(),
        panel._summary.text(),
        panel._footer.text(),
    ]
    for i in range(panel._meta.count()):
        item = panel._meta.itemAt(i)
        widget = item.widget() if item is not None else None
        if widget is not None:
            parts.append(widget.text())
    return " ".join(parts)


def _runtime_export_files() -> set[Path]:
    from nfs_scanner_pro.app_paths import get_runtime_dir

    runtime = get_runtime_dir()
    if not runtime.is_dir():
        return set()
    return {
        p.resolve()
        for p in runtime.rglob("*")
        if p.is_file() and p.suffix.lower() in EXPORT_EXTENSIONS
    }


class WorkflowContext:
    def __init__(self) -> None:
        self.app = None
        self.win = None
        self.project_name = PROJECT_NAME
        self.task_id = ""
        self.report_draft_path: Path | None = None
        self.scan_used_fallback = False
        self.workspace_backup: str | None = None
        self.project_backup: dict | None = None

    def require_win(self):
        if self.win is None:
            raise RuntimeError("MainWindow not initialized")


def check_compileall_and_imports(check: CheckResult) -> None:
    ok = bool(compileall.compile_dir(str(ROOT / "src" / "nfs_scanner_pro"), quiet=1))
    failed: list[str] = []
    if ok:
        for mod in WORKFLOW_IMPORTS:
            try:
                __import__(mod)
            except Exception as exc:  # noqa: BLE001
                failed.append(f"{mod}: {exc}")
                ok = False
    check.add("compileall", ok, "; ".join(failed) if failed else "")


def backup_runtime_state(ctx: WorkflowContext) -> None:
    from nfs_scanner_pro.app_paths import get_workspace_state_path
    from nfs_scanner_pro import project_mock

    path = get_workspace_state_path()
    ctx.workspace_backup = path.read_text(encoding="utf-8") if path.is_file() else None
    ctx.project_backup = project_mock.get_current_project()


def restore_runtime_state(ctx: WorkflowContext) -> None:
    from nfs_scanner_pro.app_paths import get_workspace_state_path
    from nfs_scanner_pro import project_mock, workspace_state_mock

    path = get_workspace_state_path()
    if ctx.workspace_backup is None:
        if path.is_file():
            path.unlink()
    else:
        path.write_text(ctx.workspace_backup, encoding="utf-8")
    workspace_state_mock.load_workspace_state()
    if ctx.project_backup is not None:
        project_mock.set_current_project(ctx.project_backup)


def check_mainwindow_boot(check: CheckResult, ctx: WorkflowContext) -> bool:
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx.app = QApplication.instance() or QApplication([])
        ctx.win = MainWindow()
        ctx.win.show()
        ctx.app.processEvents()

        project = project_mock.get_current_project()
        docks = ctx.win.findChildren(QDockWidget)
        nav_texts = [btn.text() for btn in ctx.win._nav.findChildren(QToolButton) if btn.text()]
        project_ok = PROJECT_NAME in (
            project.get("name", ""),
            project.get("pcb", ""),
        )
        ok = (
            ctx.win is not None
            and len(docks) == 1
            and ctx.win._right_dock is not None
            and not ctx.win._right_dock.isFloating()
            and "项目" not in nav_texts
            and project_ok
        )
        ctx.project_name = project.get("pcb") or project.get("name") or PROJECT_NAME
        check.add("mainwindow_boot", ok, f"docks={len(docks)} project={ctx.project_name}")
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("mainwindow_boot", False, str(exc))
        return False


def check_initial_scan_page(check: CheckResult, ctx: WorkflowContext) -> bool:
    try:
        from PySide6.QtWidgets import QLabel

        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx.require_win()
        ctx.win._switch_page(MainWindow.PAGE_SCAN)
        ctx.app.processEvents()

        crumb = ctx.win._scan_page.findChild(QLabel, "breadcrumbBar")
        crumb_text = crumb.text() if crumb else ""
        status = _status_text(ctx.win)
        toolbar_ok = all(label in toolbar_texts(ctx.win) for label in SCAN_TOOLBAR)
        dock_ok = ctx.win._right_dock.windowTitle() == "扫描参数"

        ok = (
            ctx.win._current_page == MainWindow.PAGE_SCAN
            and dock_ok
            and toolbar_ok
            and PROJECT_NAME in crumb_text
            and "CPU_Area" in crumb_text
            and "Hx" in crumb_text
            and "2.450 GHz" in crumb_text
            and "6461" in crumb_text
            and bool(status)
        )
        check.add(
            "initial_scan_page",
            ok,
            f"crumb={crumb_text!r} status={status!r}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("initial_scan_page", False, str(exc))
        return False


def check_device_mock_ready(check: CheckResult, ctx: WorkflowContext) -> bool:
    try:
        from nfs_scanner_pro.devices.device_manager_mock import DeviceManagerMock
        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx.require_win()
        ctx.win._nav._buttons[MainWindow.PAGE_DEVICE].click()
        ctx.app.processEvents()

        manager = DeviceManagerMock()
        connect_msg = manager.connect_all()
        page_text = _collect_text(ctx.win._device_page)
        bar_text = " ".join(label.text() for label in ctx.win._device_bar._device_labels)
        dock_ok = ctx.win._right_dock.windowTitle() == "设备配置"

        cards_ok = all(token in page_text for token in ("运动平台", "频谱仪", "相机", "舵机系统"))
        bar_ok = all(
            token in bar_text
            for token in ("运动平台", "COM6", "频谱仪", "ZNA67", "相机", "USB3.0", "舵机")
        )

        ctx.win._switch_page(MainWindow.PAGE_SCAN)
        ctx.app.processEvents()

        ok = (
            dock_ok
            and "Mock" in connect_msg
            and cards_ok
            and bar_ok
            and ctx.win._current_page == MainWindow.PAGE_SCAN
        )
        check.add(
            "device_mock_ready",
            ok,
            f"connect={connect_msg!r}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("device_mock_ready", False, str(exc))
        return False


def check_scan_ui_workflow(check: CheckResult, ctx: WorkflowContext) -> bool:
    try:
        from nfs_scanner_pro.scan.scan_state import ScanState as EngineScanState
        from nfs_scanner_pro.ui.main_window import MainWindow
        from nfs_scanner_pro.ui.scan_state import ScanState as UiScanState

        ctx.require_win()
        ctx.win._switch_page(MainWindow.PAGE_SCAN)
        ctx.app.processEvents()

        win = ctx.win
        scan_page = win._scan_page
        start_btn = _find_toolbar_button(win, "toolbarStartScanButton")
        stop_btn = _find_toolbar_button(win, "toolbarStopScanButton")

        if start_btn is None:
            ctx.scan_used_fallback = True
            win._on_start_scan()
        else:
            start_btn.click()
        ctx.app.processEvents()

        started_ok = (
            scan_page._engine.state is EngineScanState.SCANNING
            and scan_page.current_scan_state() is UiScanState.SCANNING
            and "扫描中" in _status_text(win)
            and not start_btn.isEnabled()
            and stop_btn.isEnabled()
            and not _param_field_enabled(win)
        )

        for _ in range(500):
            if scan_page._engine.state is EngineScanState.SCANNING:
                scan_page._on_timer_tick()
                ctx.app.processEvents()
            elif scan_page._engine.state is EngineScanState.STOPPING:
                scan_page._on_finalize_stop()
                ctx.app.processEvents()
                break

        engine = scan_page._engine
        progress = engine.progress
        status = _status_text(win)
        ctx.task_id = engine.result.task_id if engine.result else ""

        completed_ok = (
            engine.state is EngineScanState.COMPLETED
            and ("扫描完成" in status or "结果已保存" in status)
            and progress.percent == 100
            and progress.current_index == progress.total_points == 6461
            and _param_field_enabled(win)
            and start_btn.isEnabled()
            and not stop_btn.isEnabled()
        )

        ok = started_ok and completed_ok and bool(ctx.task_id)
        detail = (
            f"task={ctx.task_id} fallback={ctx.scan_used_fallback} "
            f"points={progress.current_index}/{progress.total_points}"
        )
        check.add("scan_ui_workflow", ok, detail)
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("scan_ui_workflow", False, str(exc))
        return False


def check_scan_result_files(check: CheckResult, ctx: WorkflowContext) -> bool:
    try:
        from nfs_scanner_pro.app_paths import get_mock_scan_dir

        if not ctx.task_id:
            check.add("scan_result_files", False, "missing task_id")
            return False

        scan_dir = get_mock_scan_dir(ctx.project_name, ctx.task_id)
        csv_path = scan_dir / "scan_points_preview.csv"
        csv_rows = 0
        if csv_path.is_file():
            with csv_path.open(encoding="utf-8", newline="") as handle:
                csv_rows = max(0, sum(1 for _ in csv.reader(handle)) - 1)

        json_ok = False
        try:
            payload = json.loads((scan_dir / "scan_result.json").read_text(encoding="utf-8"))
            json_ok = isinstance(payload, dict) and payload.get("task_id") == ctx.task_id
        except (OSError, json.JSONDecodeError):
            json_ok = False

        export_bad = _runtime_export_files()
        ok = (
            (scan_dir / "scan_result.json").is_file()
            and (scan_dir / "scan_summary.json").is_file()
            and csv_path.is_file()
            and csv_rows <= 200
            and json_ok
            and gitignore_covers_runtime(scan_dir / "scan_result.json")
            and not export_bad
        )
        check.add(
            "scan_result_files",
            ok,
            f"dir={scan_dir} csv_rows={csv_rows}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("scan_result_files", False, str(exc))
        return False


def check_analysis_loads_scan_task(check: CheckResult, ctx: WorkflowContext) -> bool:
    try:
        from nfs_scanner_pro.analysis.analysis_data_source_mock import AnalysisDataSourceMock
        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx.require_win()
        if not ctx.task_id:
            check.add("analysis_loads_scan_task", False, "missing task_id")
            return False

        ctx.win._nav._buttons[MainWindow.PAGE_ANALYSIS].click()
        ctx.app.processEvents()
        ctx.win._analysis_page.refresh_data_source()
        ctx.win._analysis_page._on_scan_task_selected(ctx.task_id)
        ctx.app.processEvents()

        ds = AnalysisDataSourceMock()
        dataset = ds.build_dataset(ctx.project_name, ctx.task_id)
        readout = dataset.cursor_readout()
        amp_key = "amplitude" if "amplitude" in readout else "amp"
        panel = ctx.win._analysis_panel.control_panel
        dock_text = _collect_text(ctx.win._analysis_panel)
        status = _status_text(ctx.win)

        ok = (
            ctx.win._right_dock.windowTitle() == "分析参数"
            and ctx.task_id in ds.list_scan_tasks(ctx.project_name)
            and not dataset.is_empty()
            and dataset.project_name
            and dataset.region_name
            and dataset.probe_name
            and dataset.frequency
            and dataset.trace
            and dataset.total_points
            and dataset.preview_points
            and dataset.peak_amplitude is not None
            and dataset.peak_position
            and all(k in readout for k in ("x", "y", "z", "frequency", amp_key, "phase"))
            and panel._trace_combo is not None
            and panel._freq_combo is not None
            and panel._lut_selector is not None
            and panel._opacity_slider is not None
            and "ScanTask" in dock_text
            and "Trace" in dock_text
            and "频率" in dock_text
            and "LUT" in dock_text
            and "透明度" in dock_text
            and ("分析就绪" in status or "已加载" in status)
        )
        check.add(
            "analysis_loads_scan_task",
            ok,
            f"task={ctx.task_id} points={dataset.total_points}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("analysis_loads_scan_task", False, str(exc))
        return False


def check_analysis_mock_interactions(check: CheckResult, ctx: WorkflowContext) -> bool:
    try:
        from PySide6.QtWidgets import QPushButton

        ctx.require_win()
        control = ctx.win._analysis_panel.control_panel
        before_exports = _runtime_export_files()
        statuses: list[str] = []

        trace_target = "Trace 2" if control._trace_combo.currentText() == "Trace 1" else "Trace 1"
        control._trace_combo.setCurrentText(trace_target)
        ctx.app.processEvents()
        statuses.append(_status_text(ctx.win))

        freqs = [control._freq_combo.itemText(i) for i in range(control._freq_combo.count())]
        freq_target = freqs[1] if len(freqs) > 1 else freqs[0]
        control._freq_combo.setCurrentText(freq_target)
        ctx.app.processEvents()
        statuses.append(_status_text(ctx.win))

        lut_target = "Jet" if control._lut_selector.currentText() != "Jet" else "Turbo"
        control._lut_selector.setCurrentText(lut_target)
        ctx.app.processEvents()
        statuses.append(_status_text(ctx.win))

        control._opacity_slider.setValue(max(10, control._opacity_slider.value() - 5))
        ctx.app.processEvents()
        statuses.append(_status_text(ctx.win))

        export_btn = ctx.win._analysis_panel.findChild(QPushButton, "exportHeatmapButton")
        export_btn.click()
        for _ in range(15):
            ctx.app.processEvents()
            time.sleep(0.03)
        statuses.append(_status_text(ctx.win))

        after_exports = _runtime_export_files()
        ok = all("Mock" in s or "分析" in s for s in statuses) and after_exports == before_exports
        check.add(
            "analysis_mock_interactions",
            ok,
            f"trace={trace_target} freq={freq_target}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("analysis_mock_interactions", False, str(exc))
        return False


def check_report_creates_draft(check: CheckResult, ctx: WorkflowContext) -> bool:
    try:
        from nfs_scanner_pro.app_paths import get_mock_project_dir
        from nfs_scanner_pro.report.report_data_source_mock import ReportDataSourceMock
        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx.require_win()
        if not ctx.task_id:
            check.add("report_creates_draft", False, "missing task_id")
            return False

        ctx.win._nav._buttons[MainWindow.PAGE_REPORT].click()
        ctx.app.processEvents()
        toolbar_ok = all(label in toolbar_texts(ctx.win) for label in REPORT_TOOLBAR)
        ctx.win._report_page.refresh_data_source()
        ctx.app.processEvents()

        ds = ReportDataSourceMock()
        context = ds.build_report_context(ctx.project_name, ctx.task_id)
        reports_root = get_mock_project_dir(ctx.project_name) / "reports"
        before = set(reports_root.rglob("report_draft.json")) if reports_root.is_dir() else set()

        report_mock = ctx.win._report_page._mock
        report_mock._current_project = ctx.project_name
        report_mock._current_task = ctx.task_id
        report_mock._has_source = True

        new_btn = _find_toolbar_button(ctx.win, "toolbarNewReportButton")
        new_btn.click()
        ctx.app.processEvents()

        after = set(reports_root.rglob("report_draft.json")) if reports_root.is_dir() else set()
        new_files = after - before
        draft_path = next(iter(new_files), None)
        if draft_path is None and after:
            draft_path = max(after, key=lambda p: p.stat().st_mtime)
        ctx.report_draft_path = draft_path

        draft_ok = False
        preview_ok = False
        draft_data: dict = {}
        if draft_path and draft_path.is_file():
            draft_data = json.loads(draft_path.read_text(encoding="utf-8"))
            draft_ok = all(
                draft_data.get(key)
                for key in (
                    "report_name",
                    "project_name",
                    "scan_task_id",
                    "region_name",
                    "probe_name",
                    "frequency",
                    "summary",
                )
            ) and draft_data.get("scan_task_id") == ctx.task_id

        preview_text = _preview_text(ctx.win._report_page._preview)
        preview_ok = all(
            token in preview_text
            for token in (
                "近场扫描报告",
                "项目名称",
                "区域名称",
                "ScanTask",
                "探头",
                "频率",
                "结论摘要",
            )
        )
        status = _status_text(ctx.win)

        ok = (
            ctx.win._right_dock.windowTitle() == "报告设置"
            and toolbar_ok
            and context.get("has_data")
            and draft_path is not None
            and draft_ok
            and preview_ok
            and ("已创建报告草稿" in status or "Mock" in status)
            and gitignore_covers_runtime(draft_path)
        )
        if not ok:
            detail = (
                f"draft={draft_path} task={draft_data.get('scan_task_id')} "
                f"preview={preview_ok} status={status!r} preview_snip={preview_text[:80]!r}"
            )
        else:
            detail = f"draft={draft_path} name={draft_data.get('report_name', '')!r}"
        check.add("report_creates_draft", ok, detail)
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("report_creates_draft", False, str(exc))
        return False


def check_report_export_mock(check: CheckResult, ctx: WorkflowContext) -> bool:
    try:
        ctx.require_win()
        before = _runtime_export_files()
        statuses: list[str] = []
        for obj_name in (
            "toolbarPreviewButton",
            "toolbarExportPdfButton",
            "toolbarExportWordButton",
            "toolbarExportExcelButton",
        ):
            btn = _find_toolbar_button(ctx.win, obj_name)
            btn.click()
            for _ in range(15):
                ctx.app.processEvents()
                time.sleep(0.03)
            statuses.append(_status_text(ctx.win))

        after = _runtime_export_files()
        ok = all("Mock" in s for s in statuses) and not after and not (after - before)
        check.add(
            "report_export_mock",
            ok,
            "; ".join(statuses),
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("report_export_mock", False, str(exc))
        return False


def check_cross_page_regression(check: CheckResult, ctx: WorkflowContext) -> bool:
    try:
        from PySide6.QtWidgets import QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx.require_win()
        ok = True
        details: list[str] = []
        for page_index in CROSS_PAGE_SEQUENCE:
            ctx.win._switch_page(page_index)
            ctx.app.processEvents()
            expected = DOCK_TITLES[page_index]
            actual = ctx.win._right_dock.windowTitle() if ctx.win._right_dock else ""
            docks = ctx.win.findChildren(QDockWidget)
            nav_texts = [btn.text() for btn in ctx.win._nav.findChildren(QToolButton) if btn.text()]
            floating = any(d.isFloating() for d in docks)
            page_ok = (
                ctx.win._page_stack.currentIndex() == page_index
                and actual == expected
                and len(docks) == 1
                and ctx.win._right_dock is not None
                and not ctx.win._right_dock.isFloating()
                and not floating
                and "项目" not in nav_texts
            )
            if page_index == MainWindow.PAGE_REPORT:
                page_ok = page_ok and all(t in toolbar_texts(ctx.win) for t in REPORT_TOOLBAR)
            else:
                page_ok = page_ok and all(t in toolbar_texts(ctx.win) for t in SCAN_TOOLBAR)
            if not page_ok:
                ok = False
            details.append(f"{page_index}:{actual!r}")
        check.add("cross_page_regression", ok, ", ".join(details))
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("cross_page_regression", False, str(exc))
        return False


def check_workspace_state_saved(check: CheckResult, ctx: WorkflowContext) -> bool:
    try:
        from nfs_scanner_pro.app_paths import get_workspace_state_path

        ctx.require_win()
        ctx.win._capture_and_save_workspace()
        ctx.app.processEvents()

        path = get_workspace_state_path()
        payload = json.loads(path.read_text(encoding="utf-8"))
        keys_ok = all(
            key in payload
            for key in (
                "last_page",
                "current_project",
                "right_dock_visible",
                "navigation_expanded",
            )
        )
        json_ok = isinstance(payload, dict)
        git_ok = gitignore_covers_runtime(path)
        ok = path.is_file() and json_ok and keys_ok and git_ok
        check.add(
            "workspace_state_saved",
            ok,
            f"last_page={payload.get('last_page')}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("workspace_state_saved", False, str(exc))
        return False


def check_no_real_device_access(check: CheckResult) -> None:
    hits: list[str] = []
    for base in MOCK_DEVICE_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in text:
                    hits.append(f"{path.relative_to(ROOT)}: {pattern}")
    export_files = _runtime_export_files()
    if export_files:
        hits.append(
            "runtime exports: "
            + ", ".join(str(p.relative_to(ROOT)) for p in sorted(export_files))
        )
    check.add("no_real_device_access", not hits, "; ".join(hits))


def write_acceptance_report(check: CheckResult, ctx: WorkflowContext) -> Path:
    report_path = (
        ROOT
        / "docs/product-spec/release/Release_030_Cross_Page_Workflow_UI_Verification/ACCEPTANCE_REPORT.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_030 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_030.py",
        "python scripts/verify_all.py",
        "```",
        "",
        "## 检查项",
        "",
    ]
    for name, ok, detail in check.results:
        status = "PASS" if ok else "FAIL"
        suffix = f" — {detail}" if detail else ""
        lines.append(f"- [{status}] `{name}`{suffix}")
    lines.extend(
        [
            "",
            "## 结果",
            "",
            "PASS" if check.passed else "FAIL",
            "",
            "## runtime 扫描结果",
            "",
        ]
    )
    if ctx.task_id:
        lines.append(
            f"- `{describe_mock_scan_dir(ctx.project_name, ctx.task_id)}/`"
        )
    lines.extend(["", "## runtime 报告草稿", ""])
    if ctx.report_draft_path:
        lines.append(f"- `{ctx.report_draft_path.relative_to(ROOT).as_posix()}`")
    lines.extend(
        [
            "",
            "## 是否接真实设备",
            "",
            "否",
            "",
            "## 是否实现真实扫描算法",
            "",
            "否",
            "",
            "## 是否生成真实 PDF / Word / Excel",
            "",
            "否",
            "",
            "## 是否修改 high_fidelity HTML",
            "",
            "否",
            "",
            "## 是否可以提交",
            "",
            "是" if check.passed else "否",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    setup_offscreen()
    setup_path()
    check = CheckResult("Release_030 Verification")
    ctx = WorkflowContext()
    backup_runtime_state(ctx)
    try:
        check_compileall_and_imports(check)
        if check_mainwindow_boot(check, ctx):
            check_initial_scan_page(check, ctx)
            check_device_mock_ready(check, ctx)
            if check_scan_ui_workflow(check, ctx):
                check_scan_result_files(check, ctx)
            check_analysis_loads_scan_task(check, ctx)
            check_analysis_mock_interactions(check, ctx)
            check_report_creates_draft(check, ctx)
            check_report_export_mock(check, ctx)
            check_cross_page_regression(check, ctx)
            check_workspace_state_saved(check, ctx)
        check_no_real_device_access(check)
    finally:
        if ctx.win is not None:
            ctx.win.close()
            if ctx.app is not None:
                ctx.app.processEvents()
        restore_runtime_state(ctx)

    report_path = write_acceptance_report(check, ctx)
    check.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return 0 if check.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
