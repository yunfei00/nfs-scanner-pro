#!/usr/bin/env python3
"""Release_024 自动验收 — Full Workflow Smoke Test。"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from verification_utils import (  # noqa: E402
    DOCK_TITLES,
    FORBIDDEN_PATTERNS,
    MOCK_DEVICE_DIRS,
    NAV_LABELS,
    PROJECT_NAME,
    REPORT_TOOLBAR,
    ROOT,
    CheckResult,
    describe_mock_report_draft,
    describe_mock_scan_dir,
    describe_workspace_state,
    gitignore_covers_runtime,
    setup_offscreen,
    setup_path,
    toolbar_texts,
)

REPORT_DRAFT_ID = "RP-SMOKE-024"
WORKFLOW_SEQUENCE = (0, 1, 2, 3, 0)


class WorkflowSmokeContext:
    def __init__(self, check: CheckResult) -> None:
        self.check = check
        self.app = None
        self.win = None
        self.task_id = ""
        self.project_name = PROJECT_NAME
        self.scan_messages: list[str] = []
        self.workspace_backup: str | None = None
        self.project_backup: dict | None = None

    def _require_win(self):
        if self.win is None:
            raise RuntimeError("MainWindow not initialized")


def check_mainwindow_boot(ctx: WorkflowSmokeContext) -> None:
    try:
        from PySide6.QtWidgets import QApplication

        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx.app = QApplication.instance() or QApplication([])
        ctx.win = MainWindow()
        ctx.win.show()
        ctx.app.processEvents()
        ok = ctx.win is not None and ctx.win._page_stack is not None
        ctx.check.add("mainwindow_boot", ok, f"page={ctx.win._current_page}")
    except Exception as exc:  # noqa: BLE001
        ctx.check.add("mainwindow_boot", False, str(exc))


def check_project_prepare(ctx: WorkflowSmokeContext) -> None:
    try:
        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui import mock_data

        ctx._require_win()
        ctx.project_backup = project_mock.get_current_project()
        current = project_mock.get_current_project()
        if current.get("status") == "closed" or not current.get("name"):
            project_mock.create_project_mock(
                PROJECT_NAME,
                f"D:/NFS_Projects/{PROJECT_NAME}",
                PROJECT_NAME,
                "CPU_Area",
            )
        else:
            project_mock.open_project_mock(PROJECT_NAME)
        mock_data.apply_project(project_mock.get_current_project())
        ctx.win._refresh_project_ui()
        ctx.app.processEvents()

        project = project_mock.get_current_project()
        recent = project_mock.get_recent_projects()
        title_ok = PROJECT_NAME in ctx.win.windowTitle()
        from PySide6.QtWidgets import QLabel

        scan_crumb = ctx.win._scan_page.findChild(QLabel, "breadcrumbBar")
        breadcrumb_ok = scan_crumb is not None and PROJECT_NAME in scan_crumb.text()
        ok = (
            project.get("name") == PROJECT_NAME
            and bool(recent)
            and title_ok
            and breadcrumb_ok
        )
        ctx.project_name = project.get("pcb") or project.get("name") or PROJECT_NAME
        ctx.check.add(
            "project_prepare",
            ok,
            f"project={project.get('name')} recent={len(recent)}",
        )
    except Exception as exc:  # noqa: BLE001
        ctx.check.add("project_prepare", False, str(exc))


def check_workspace_state(ctx: WorkflowSmokeContext) -> None:
    try:
        from nfs_scanner_pro.app_paths import get_workspace_state_path
        from nfs_scanner_pro import workspace_state_mock

        path = get_workspace_state_path()
        ctx.workspace_backup = path.read_text(encoding="utf-8") if path.is_file() else None

        state, load_ok = workspace_state_mock.load_workspace_state()
        keys_ok = all(
            k in state for k in ("last_page", "navigation_expanded", "right_dock_visible")
        )
        workspace_state_mock.save_workspace_state(state)
        file_ok = path.is_file()
        git_ok = gitignore_covers_runtime(path)
        ok = load_ok and keys_ok and file_ok and git_ok
        ctx.check.add(
            "workspace_state",
            ok,
            f"last_page={state.get('last_page')} gitignored={git_ok}",
        )
    except Exception as exc:  # noqa: BLE001
        ctx.check.add("workspace_state", False, str(exc))


def check_device_mock(ctx: WorkflowSmokeContext) -> None:
    try:
        from nfs_scanner_pro.devices.device_manager_mock import get_device_manager

        mgr = get_device_manager()
        connect_msg = mgr.connect_all()
        x_before = mgr.motion.x
        mgr.motion.jog("x", "+")
        servo_msg = mgr.servo.switch_to_hy()
        camera_msg = mgr.camera.capture()
        snapshot = mgr.get_snapshot()
        all_connected = all(
            mgr.get_device(key).is_connected()
            for key in ("motion", "spectrum", "camera", "servo")
        )
        ok = (
            "Mock" in connect_msg
            and all_connected
            and mgr.motion.x > x_before
            and "Mock" in servo_msg
            and "Mock" in camera_msg
            and all(k in snapshot for k in ("motion", "spectrum", "camera", "servo"))
        )
        ctx.check.add("device_mock", ok)
    except Exception as exc:  # noqa: BLE001
        ctx.check.add("device_mock", False, str(exc))


def check_scan_engine(ctx: WorkflowSmokeContext) -> None:
    try:
        from nfs_scanner_pro.scan import ScanState, ScanTaskConfig, get_scan_engine

        ctx._require_win()
        engine = get_scan_engine()
        config = ScanTaskConfig.from_mock_data()
        config.project_name = ctx.project_name
        engine.on_message(lambda msg: ctx.scan_messages.append(msg))
        engine.prepare(config)
        states_seen: list[ScanState] = [engine.state]
        engine.start()
        states_seen.append(engine.state)
        index_before = engine.progress.current_index

        for _ in range(500):
            if engine.state is ScanState.SCANNING:
                engine.tick()
                if engine.state not in states_seen:
                    states_seen.append(engine.state)
            elif engine.state is ScanState.STOPPING:
                engine.finalize_stop()
                states_seen.append(engine.state)
                break

        point = engine.current_point() or engine.progress.current_point
        result = engine.result
        state_ok = (
            ScanState.READY in states_seen
            and ScanState.SCANNING in states_seen
            and engine.state is ScanState.COMPLETED
        )
        index_ok = engine.progress.current_index >= index_before
        total_ok = engine.config.total_points == config.total_points
        result_ok = (
            result is not None
            and bool(result.device_snapshot)
            and result.config.frequency
            and point is not None
            and hasattr(point, "amplitude")
        )
        ctx.task_id = result.task_id if result else ""
        ok = state_ok and index_ok and total_ok and result_ok and bool(ctx.task_id)
        ctx.check.add(
            "scan_engine",
            ok,
            f"task={ctx.task_id} points={engine.progress.current_index}/{config.total_points}",
        )
    except Exception as exc:  # noqa: BLE001
        ctx.check.add("scan_engine", False, str(exc))


def check_scan_result_persistence(ctx: WorkflowSmokeContext) -> None:
    try:
        from nfs_scanner_pro.app_paths import get_mock_scan_dir

        if not ctx.task_id:
            ctx.check.add("scan_result_persistence", False, "missing task_id")
            return

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

        saved_msg = any("结果已保存" in msg or "扫描结果已保存" in msg for msg in ctx.scan_messages)
        export_bad = (
            list(scan_dir.glob("*.pdf"))
            + list(scan_dir.glob("*.docx"))
            + list(scan_dir.glob("*.xlsx"))
        )
        ok = (
            (scan_dir / "scan_result.json").is_file()
            and (scan_dir / "scan_summary.json").is_file()
            and csv_path.is_file()
            and csv_rows <= 200
            and json_ok
            and saved_msg
            and not export_bad
            and gitignore_covers_runtime(scan_dir / "scan_result.json")
        )
        ctx.check.add(
            "scan_result_persistence",
            ok,
            f"dir={scan_dir.name} csv_rows={csv_rows} msg={saved_msg}",
        )
    except Exception as exc:  # noqa: BLE001
        ctx.check.add("scan_result_persistence", False, str(exc))


def check_analysis_page(ctx: WorkflowSmokeContext) -> None:
    try:
        from PySide6.QtWidgets import QDockWidget

        from nfs_scanner_pro.analysis.analysis_data_source_mock import AnalysisDataSourceMock
        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx._require_win()
        if not ctx.task_id:
            ctx.check.add("analysis_page", False, "missing task_id")
            return

        ctx.win._switch_page(MainWindow.PAGE_ANALYSIS)
        ctx.app.processEvents()
        dock_title = ctx.win._right_dock.windowTitle() if ctx.win._right_dock else ""
        ctx.win._analysis_page.refresh_data_source()
        if ctx.task_id in ctx.win._analysis_page._current_tasks:
            ctx.win._analysis_page._on_scan_task_selected(ctx.task_id)
        ctx.app.processEvents()

        ds = AnalysisDataSourceMock()
        dataset = ds.build_dataset(ctx.project_name, ctx.task_id)
        readout = dataset.cursor_readout()
        empty = ds.build_dataset("MissingProject_XYZ", "ST-MISSING")
        amp_key = "amplitude" if "amplitude" in readout else "amp"
        ui_dataset = ctx.win._analysis_page._mock.dataset

        ok = (
            dock_title == "分析参数"
            and not dataset.is_empty()
            and dataset.project_name
            and dataset.task_id == ctx.task_id
            and dataset.frequency
            and dataset.trace
            and amp_key in readout
            and dataset.source_path
            and empty.is_empty()
            and ui_dataset.task_id == ctx.task_id
        )
        ctx.check.add(
            "analysis_page",
            ok,
            f"dock={dock_title!r} task={dataset.task_id} trace={dataset.trace}",
        )
        _ = QDockWidget
    except Exception as exc:  # noqa: BLE001
        ctx.check.add("analysis_page", False, str(exc))


def check_report_page(ctx: WorkflowSmokeContext) -> None:
    try:
        from nfs_scanner_pro.report.report_data_source_mock import ReportDataSourceMock
        from nfs_scanner_pro.report.report_draft_mock import ReportDraftMock
        from nfs_scanner_pro.report.report_persistence_mock import ReportPersistenceMock
        from nfs_scanner_pro.report.report_preview_model import ReportPreviewModel
        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx._require_win()
        if not ctx.task_id:
            ctx.check.add("report_page", False, "missing task_id")
            return

        ctx.win._switch_page(MainWindow.PAGE_REPORT)
        ctx.app.processEvents()
        dock_title = ctx.win._right_dock.windowTitle() if ctx.win._right_dock else ""
        toolbar_ok = all(label in toolbar_texts(ctx.win) for label in REPORT_TOOLBAR)
        ctx.win._report_page.refresh_data_source()
        ctx.app.processEvents()

        ds = ReportDataSourceMock()
        context = ds.build_report_context(ctx.project_name, ctx.task_id)
        settings = ctx.win._report_panel.get_settings()
        draft = ReportDraftMock.from_analysis_dataset(context["dataset"], settings)
        draft.report_id = REPORT_DRAFT_ID
        persistence = ReportPersistenceMock()
        saved, _ = persistence.save_draft(draft)
        report_dir = persistence.build_report_dir(ctx.project_name, REPORT_DRAFT_ID)
        draft_path = report_dir / ReportPersistenceMock.DRAFT_FILENAME
        preview = ReportPreviewModel.from_draft(draft)
        export_bad = (
            list(report_dir.glob("*.pdf"))
            + list(report_dir.glob("*.docx"))
            + list(report_dir.glob("*.xlsx"))
        )

        ok = (
            dock_title == "报告设置"
            and toolbar_ok
            and context.get("has_data")
            and bool(draft.report_name)
            and bool(preview.title)
            and saved
            and draft_path.is_file()
            and not export_bad
            and gitignore_covers_runtime(draft_path)
        )
        ctx.check.add(
            "report_page",
            ok,
            f"dock={dock_title!r} draft={draft_path.name}",
        )
    except Exception as exc:  # noqa: BLE001
        ctx.check.add("report_page", False, str(exc))


def check_page_switch_regression(ctx: WorkflowSmokeContext) -> None:
    try:
        from PySide6.QtWidgets import QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx._require_win()
        ok = True
        details: list[str] = []
        for page_index in WORKFLOW_SEQUENCE:
            ctx.win._switch_page(page_index)
            ctx.app.processEvents()
            expected_dock = DOCK_TITLES[page_index]
            actual_dock = ctx.win._right_dock.windowTitle() if ctx.win._right_dock else ""
            stack_ok = ctx.win._page_stack.currentIndex() == page_index
            dock_ok = actual_dock == expected_dock
            docks = ctx.win.findChildren(QDockWidget)
            single_dock = len(docks) == 1
            not_floating = ctx.win._right_dock is not None and not ctx.win._right_dock.isFloating()
            nav_texts = [
                btn.text() for btn in ctx.win._nav.findChildren(QToolButton) if btn.text()
            ]
            no_project = "项目" not in nav_texts
            if not (stack_ok and dock_ok and single_dock and not_floating and no_project):
                ok = False
            details.append(f"{page_index}:{actual_dock!r}:stack={stack_ok}")
        ctx.check.add("page_switch_regression", ok, ", ".join(details))
        ctx.win.close()
    except Exception as exc:  # noqa: BLE001
        ctx.check.add("page_switch_regression", False, str(exc))


def check_no_real_device_access(check: CheckResult) -> None:
    hits: list[str] = []
    for base in MOCK_DEVICE_DIRS:
        if not base.exists():
            continue
        paths = [base] if base.is_file() else base.rglob("*.py")
        for path in paths:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in text:
                    hits.append(f"{path.relative_to(ROOT)}: {pattern}")
    check.add("no_real_device_access", not hits, "; ".join(hits))


def restore_workspace(ctx: WorkflowSmokeContext) -> None:
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


def write_acceptance_report(check: CheckResult, ctx: WorkflowSmokeContext) -> Path:
    report_path = (
        ROOT
        / "docs/product-spec/release/Release_024_Full_Workflow_Smoke_Test/ACCEPTANCE_REPORT.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_024 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_024.py",
        "python scripts/verify_all.py",
        "```",
        "",
        "## 验收项",
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
            "## runtime 产物",
            "",
            f"- `{describe_workspace_state()}`",
        ]
    )
    if ctx.task_id:
        lines.append(
            f"- `{describe_mock_scan_dir(ctx.project_name, ctx.task_id)}/`"
        )
    lines.append(
        f"- `{describe_mock_report_draft(ctx.project_name, REPORT_DRAFT_ID)}`"
    )
    lines.extend(
        [
            "",
            "## 是否接真实设备",
            "",
            "否",
            "",
            "## 是否生成真实 PDF / Word / Excel",
            "",
            "否",
            "",
            "## 是否允许提交",
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
    check = CheckResult("Release_024 Verification")
    ctx = WorkflowSmokeContext(check)
    try:
        check_mainwindow_boot(ctx)
        check_project_prepare(ctx)
        check_workspace_state(ctx)
        check_device_mock(ctx)
        check_scan_engine(ctx)
        check_scan_result_persistence(ctx)
        check_analysis_page(ctx)
        check_report_page(ctx)
        check_page_switch_regression(ctx)
        check_no_real_device_access(check)
    finally:
        restore_workspace(ctx)
    report_path = write_acceptance_report(check, ctx)
    check.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return 0 if check.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
