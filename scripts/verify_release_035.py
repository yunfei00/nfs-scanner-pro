#!/usr/bin/env python3
"""Release_035 自动验收 — Scan Task Workspace Integration。"""

from __future__ import annotations

import compileall
import csv
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import verification_report  # noqa: E402
import verification_runtime  # noqa: E402
from verification_utils import (  # noqa: E402
    DOCK_TITLES,
    FORBIDDEN_PATTERNS,
    MOCK_DEVICE_DIRS,
    NAV_LABELS,
    REPORT_TOOLBAR,
    ROOT as UTILS_ROOT,
    SCAN_TOOLBAR,
    setup_path,
    toolbar_texts,
)

IMPORT_MODULES = (
    "nfs_scanner_pro.ui.main_window",
    "nfs_scanner_pro.project_mock",
    "nfs_scanner_pro.workspace_state_mock",
    "nfs_scanner_pro.scan.scan_task_config",
    "nfs_scanner_pro.scan.scan_engine_mock",
    "nfs_scanner_pro.scan.scan_result_persistence_mock",
    "nfs_scanner_pro.analysis.analysis_data_source_mock",
    "nfs_scanner_pro.report.report_data_source_mock",
    "nfs_scanner_pro.app_paths",
)

PROJECT_A = "iPhone16_Mainboard"
PROJECT_B = "RF_Module_Test"
REGION_A = "CPU_Area"
REGION_B = "RF_Area"

FORBIDDEN_SCAN_PATHS = MOCK_DEVICE_DIRS + (
    ROOT / "src/nfs_scanner_pro/ui/dialogs",
    ROOT / "src/nfs_scanner_pro/project_mock.py",
    ROOT / "src/nfs_scanner_pro/workspace_state_mock.py",
)

EXPORT_EXTENSIONS = {".pdf", ".docx", ".xlsx"}


@dataclass
class ScanSession:
    task_id_a: str = ""
    task_id_b: str = ""
    scan_dir_a: Path | None = None
    scan_dir_b: Path | None = None
    report_draft_a: Path | None = None
    report_draft_b: Path | None = None


SESSION = ScanSession()


def _process(app, rounds: int = 10) -> None:
    for _ in range(rounds):
        app.processEvents()
        time.sleep(0.02)


def _status_text(win) -> str:
    return win._status._message.text()


def _breadcrumb_scan(win) -> str:
    from PySide6.QtWidgets import QLabel

    crumb = win._scan_page.findChild(QLabel, "breadcrumbBar")
    return crumb.text() if crumb is not None else ""


def _list_shared_mock_files() -> set[str]:
    base = verification_runtime.get_shared_mock_projects_dir()
    if not base.is_dir():
        return set()
    return {p.relative_to(ROOT).as_posix() for p in base.rglob("*") if p.is_file()}


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


def _reset_isolated_runtime(*, clean: bool = True) -> Path:
    if clean:
        verification_runtime.clean_release_runtime("035")
    runtime_dir = verification_runtime.enter_release_runtime("R035")
    setup_path()
    from nfs_scanner_pro import project_mock, workspace_state_mock
    from nfs_scanner_pro.app_paths import get_workspace_state_path
    from nfs_scanner_pro.scan import ScanTaskConfig, get_scan_engine

    workspace_state_mock.reset_workspace_state()
    project_mock.apply_workspace_state(
        workspace_state_mock.DEFAULT_WORKSPACE_STATE["current_project"],
        workspace_state_mock.DEFAULT_WORKSPACE_STATE["recent_projects"],
    )
    path = get_workspace_state_path()
    if path.is_file():
        path.unlink()
    get_scan_engine().prepare(ScanTaskConfig.from_current_project())
    return runtime_dir


def _run_complete_scan(win) -> tuple[str, str]:
    from PySide6.QtWidgets import QApplication

    from nfs_scanner_pro.scan.scan_state import ScanState as EngineScanState

    win._switch_page(win.PAGE_SCAN)
    win._scan_page.start_scan_mock()
    app = QApplication.instance()
    scan_page = win._scan_page
    for _ in range(500):
        if scan_page._engine.state is EngineScanState.SCANNING:
            scan_page._on_timer_tick()
            if app:
                app.processEvents()
        elif scan_page._engine.state is EngineScanState.STOPPING:
            scan_page._on_finalize_stop()
            if app:
                app.processEvents()
            break
        time.sleep(0.005)
    task_id = scan_page._engine.result.task_id if scan_page._engine.result else ""
    project = scan_page._engine.config.project_name
    return task_id, project


def _scan_dir(project: str, task_id: str) -> Path:
    from nfs_scanner_pro.app_paths import get_mock_scan_dir

    return get_mock_scan_dir(project, task_id)


def _csv_row_count(path: Path) -> int:
    if not path.is_file():
        return 0
    with path.open(encoding="utf-8", newline="") as handle:
        return max(0, sum(1 for _ in csv.reader(handle)) - 1)


def check_compileall(report: verification_report.VerificationReport) -> None:
    report.start_check("compileall")
    ok = bool(compileall.compile_dir(str(ROOT / "src" / "nfs_scanner_pro"), quiet=1))
    failed: list[str] = []
    if ok:
        for mod in IMPORT_MODULES:
            try:
                __import__(mod)
            except Exception as exc:  # noqa: BLE001
                failed.append(f"{mod}: {exc}")
                ok = False
    if ok:
        report.pass_check("compileall")
    else:
        report.fail_check("compileall", "; ".join(failed))


def check_runtime_isolation(report: verification_report.VerificationReport) -> None:
    report.start_check("runtime_isolation")
    baseline = _list_shared_mock_files()
    before_exports = _runtime_export_files()
    try:
        runtime_dir = _reset_isolated_runtime()
        setup_path()
        from nfs_scanner_pro.app_paths import get_runtime_dir, get_mock_projects_dir, get_workspace_state_path

        active = get_runtime_dir().resolve()
        ws_path = get_workspace_state_path()
        ws_path.parent.mkdir(parents=True, exist_ok=True)
        ws_path.write_text("{}", encoding="utf-8")
        report_dir = get_mock_projects_dir() / PROJECT_A / "reports" / "RP-TEST"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "report_draft.json").write_text("{}", encoding="utf-8")

        ok = (
            active == runtime_dir.resolve()
            and "verification/R035" in active.as_posix()
            and ws_path.is_file()
            and "verification/R035" in ws_path.as_posix()
            and (report_dir / "report_draft.json").is_file()
        )
        git_ok, git_detail = verification_runtime.assert_runtime_ignored_by_git()
        after = _list_shared_mock_files()
        after_exports = _runtime_export_files()
        ok = (
            ok
            and git_ok
            and not (after - baseline)
            and not (after_exports - before_exports)
        )
        detail = ws_path.relative_to(ROOT).as_posix()
        if ok:
            report.pass_check("runtime_isolation", detail)
        else:
            report.fail_check("runtime_isolation", f"{detail}; git={git_detail}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("runtime_isolation", str(exc))


def check_mainwindow_boot(report: verification_report.VerificationReport) -> None:
    report.start_check("mainwindow_boot")
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        nav_texts = [
            btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()
        ]
        docks = win.findChildren(QDockWidget)
        ok = (
            len(docks) == 1
            and win._right_dock is not None
            and not win._right_dock.isFloating()
            and "项目" not in nav_texts
        )
        if ok:
            report.pass_check("mainwindow_boot")
        else:
            report.fail_check("mainwindow_boot", f"nav={nav_texts} docks={len(docks)}")
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("mainwindow_boot", str(exc))


def check_current_project_init(report: verification_report.VerificationReport) -> None:
    report.start_check("current_project_init")
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        project = project_mock.get_current_project()
        crumb = _breadcrumb_scan(win)
        required = ("name", "path", "pcb", "default_region", "status")
        ok = all(key in project for key in required)
        ok = ok and project.get("name") == PROJECT_A
        ok = ok and PROJECT_A in crumb
        ok = ok and "workspace" not in crumb.lower()
        if ok:
            report.pass_check("current_project_init", project.get("name", ""))
        else:
            report.fail_check("current_project_init", str(project))
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("current_project_init", str(exc))


def check_project_switch_scan_sync(report: verification_report.VerificationReport) -> None:
    report.start_check("project_switch_scan_sync")
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication, QToolButton

        from nfs_scanner_pro import project_mock, workspace_state_mock
        from nfs_scanner_pro.app_paths import get_workspace_state_path
        from nfs_scanner_pro.scan import ScanTaskConfig
        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        project_mock.open_project_mock(PROJECT_A)
        win._refresh_project_ui()
        _process(app)
        config_a = ScanTaskConfig.from_current_project()
        crumb_a = _breadcrumb_scan(win)

        project_mock.open_project_mock(PROJECT_B)
        win._refresh_project_ui()
        win._set_project_status(f"Mock：已打开项目 {PROJECT_B}")
        win._capture_and_save_workspace()
        _process(app)
        config_b = ScanTaskConfig.from_current_project()
        crumb_b = _breadcrumb_scan(win)
        status = _status_text(win)
        nav_texts = [
            btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()
        ]

        ok = (
            project_mock.get_current_project()["name"] == PROJECT_B
            and PROJECT_B in crumb_b
            and config_b.project_name == PROJECT_B
            and config_b.region_name == REGION_B
            and PROJECT_A in crumb_a
            and config_a.project_name == PROJECT_A
            and "Mock" in status
            and "已打开项目" in status
            and get_workspace_state_path().is_file()
            and "项目" not in nav_texts
        )
        if ok:
            report.pass_check("project_switch_scan_sync")
        else:
            report.fail_check(
                "project_switch_scan_sync",
                f"cfg={config_b.project_name}/{config_b.region_name} crumb={crumb_b}",
            )
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("project_switch_scan_sync", str(exc))


def check_project_a_scan_result_path(report: verification_report.VerificationReport) -> None:
    report.start_check("project_a_scan_result_path")
    SESSION.task_id_a = ""
    SESSION.scan_dir_a = None
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        project_mock.open_project_mock(PROJECT_A)
        win._refresh_project_ui()
        task_id, project = _run_complete_scan(win)
        status = _status_text(win)
        scan_dir = _scan_dir(project, task_id)
        result_path = scan_dir / "scan_result.json"
        payload = json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else {}

        ok = (
            task_id
            and project == PROJECT_A
            and result_path.is_file()
            and (scan_dir / "scan_summary.json").is_file()
            and (scan_dir / "scan_points_preview.csv").is_file()
            and payload.get("project_name") == PROJECT_A
            and _csv_row_count(scan_dir / "scan_points_preview.csv") <= 200
            and ("扫描完成" in status or "结果已保存" in status or "Mock" in status)
            and "verification/R035" in scan_dir.as_posix()
        )
        if ok:
            SESSION.task_id_a = task_id
            SESSION.scan_dir_a = scan_dir
            report.pass_check("project_a_scan_result_path", scan_dir.relative_to(ROOT).as_posix())
        else:
            report.fail_check("project_a_scan_result_path", f"task={task_id} dir={scan_dir}")
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("project_a_scan_result_path", str(exc))


def check_project_b_scan_result_path(report: verification_report.VerificationReport) -> None:
    report.start_check("project_b_scan_result_path")
    if not SESSION.task_id_a or SESSION.scan_dir_a is None:
        report.fail_check("project_b_scan_result_path", "project A scan missing")
        return
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R035")
        from PySide6.QtWidgets import QApplication

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        project_mock.open_project_mock(PROJECT_B)
        win._refresh_project_ui()
        task_id, project = _run_complete_scan(win)
        scan_dir_b = _scan_dir(project, task_id)
        result_b = json.loads((scan_dir_b / "scan_result.json").read_text(encoding="utf-8"))

        dir_a = SESSION.scan_dir_a
        ok = (
            task_id
            and project == PROJECT_B
            and result_b.get("project_name") == PROJECT_B
            and scan_dir_b.is_dir()
            and dir_a is not None
            and dir_a.is_dir()
            and (dir_a / "scan_result.json").is_file()
            and task_id != SESSION.task_id_a
            and not (scan_dir_b / "scan_result.json").samefile(dir_a / "scan_result.json")
            and "verification/R035" in scan_dir_b.as_posix()
        )
        if ok:
            SESSION.task_id_b = task_id
            SESSION.scan_dir_b = scan_dir_b
            report.pass_check("project_b_scan_result_path", scan_dir_b.relative_to(ROOT).as_posix())
        else:
            report.fail_check("project_b_scan_result_path", f"b={task_id} a={SESSION.task_id_a}")
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("project_b_scan_result_path", str(exc))


def check_scantask_config_project_binding(report: verification_report.VerificationReport) -> None:
    report.start_check("scantask_config_project_binding")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R035")
        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.scan import ScanTaskConfig

        project_mock.open_project_mock(PROJECT_A)
        cfg_a = ScanTaskConfig.from_current_project()
        project_mock.open_project_mock(PROJECT_B)
        cfg_b = ScanTaskConfig.from_current_project()

        ok = (
            cfg_a.project_name == PROJECT_A
            and cfg_a.region_name == REGION_A
            and cfg_b.project_name == PROJECT_B
            and cfg_b.region_name == REGION_B
            and cfg_a.project_name != cfg_b.project_name
        )
        detail = f"A={cfg_a.project_name}/{cfg_a.region_name} B={cfg_b.project_name}/{cfg_b.region_name}"
        if ok:
            report.pass_check("scantask_config_project_binding", detail)
        else:
            report.fail_check("scantask_config_project_binding", detail)
    except Exception as exc:  # noqa: BLE001
        report.fail_check("scantask_config_project_binding", str(exc))


def check_analysis_data_source_project_isolation(report: verification_report.VerificationReport) -> None:
    report.start_check("analysis_data_source_project_isolation")
    if not SESSION.task_id_a or not SESSION.task_id_b:
        report.fail_check("analysis_data_source_project_isolation", "missing scan tasks")
        return
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R035")
        from nfs_scanner_pro.analysis.analysis_data_source_mock import AnalysisDataSourceMock

        ds = AnalysisDataSourceMock()
        projects = ds.list_projects()
        tasks_a = ds.list_scan_tasks(PROJECT_A)
        tasks_b = ds.list_scan_tasks(PROJECT_B)
        dataset_a = ds.build_dataset(PROJECT_A, SESSION.task_id_a)
        dataset_b = ds.build_dataset(PROJECT_B, SESSION.task_id_b)

        path_a = (dataset_a.source_path or "").replace("\\", "/")
        path_b = (dataset_b.source_path or "").replace("\\", "/")
        ok = (
            PROJECT_A in projects
            and PROJECT_B in projects
            and SESSION.task_id_a in tasks_a
            and SESSION.task_id_b in tasks_b
            and SESSION.task_id_a not in tasks_b
            and SESSION.task_id_b not in tasks_a
            and not dataset_a.is_empty()
            and not dataset_b.is_empty()
            and dataset_a.project_name == PROJECT_A
            and dataset_b.project_name == PROJECT_B
            and "verification/R035" in path_a
            and "verification/R035" in path_b
        )
        if ok:
            report.pass_check("analysis_data_source_project_isolation")
        else:
            report.fail_check(
                "analysis_data_source_project_isolation",
                f"tasks_a={tasks_a} tasks_b={tasks_b}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("analysis_data_source_project_isolation", str(exc))


def check_report_data_source_project_isolation(report: verification_report.VerificationReport) -> None:
    report.start_check("report_data_source_project_isolation")
    if not SESSION.task_id_a or not SESSION.task_id_b:
        report.fail_check("report_data_source_project_isolation", "missing scan tasks")
        return
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R035")
        from nfs_scanner_pro.report.report_data_source_mock import ReportDataSourceMock
        from nfs_scanner_pro.report.report_draft_mock import ReportDraftMock
        from nfs_scanner_pro.report.report_persistence_mock import ReportPersistenceMock

        ds = ReportDataSourceMock()
        persist = ReportPersistenceMock()
        projects = ds.list_projects()
        ctx_a = ds.build_report_context(PROJECT_A, SESSION.task_id_a)
        ctx_b = ds.build_report_context(PROJECT_B, SESSION.task_id_b)
        draft_a = ReportDraftMock.from_analysis_dataset(
            ctx_a["dataset"], {}, report_name="Report_A"
        )
        draft_b = ReportDraftMock.from_analysis_dataset(
            ctx_b["dataset"], {}, report_name="Report_B"
        )
        ok_a, path_a = persist.save_draft(draft_a)
        ok_b, path_b = persist.save_draft(draft_b)
        payload_a = json.loads(Path(path_a).read_text(encoding="utf-8")) if ok_a else {}
        payload_b = json.loads(Path(path_b).read_text(encoding="utf-8")) if ok_b else {}

        ok = (
            PROJECT_A in projects
            and PROJECT_B in projects
            and SESSION.task_id_a in ds.list_scan_tasks(PROJECT_A)
            and SESSION.task_id_b in ds.list_scan_tasks(PROJECT_B)
            and ctx_a["project_name"] == PROJECT_A
            and ctx_b["project_name"] == PROJECT_B
            and ok_a
            and ok_b
            and payload_a.get("project_name") == PROJECT_A
            and payload_b.get("project_name") == PROJECT_B
            and "verification/R035" in path_a.replace("\\", "/")
            and "verification/R035" in path_b.replace("\\", "/")
            and not _runtime_export_files()
        )
        if ok:
            SESSION.report_draft_a = Path(path_a)
            SESSION.report_draft_b = Path(path_b)
            report.pass_check("report_data_source_project_isolation")
        else:
            report.fail_check("report_data_source_project_isolation", f"a={ok_a} b={ok_b}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("report_data_source_project_isolation", str(exc))


def check_workspace_project_restore(report: verification_report.VerificationReport) -> None:
    report.start_check("workspace_project_restore")
    _reset_isolated_runtime()
    try:
        from nfs_scanner_pro import project_mock, workspace_state_mock
        from nfs_scanner_pro.app_paths import get_workspace_state_path

        project_mock.open_project_mock(PROJECT_B)
        workspace_state_mock.update_current_project(project_mock.get_current_project())
        workspace_state_mock.update_recent_projects(
            [PROJECT_B, PROJECT_A, "Demo_Project_001"]
        )
        workspace_state_mock.update_last_page("scan")
        workspace_state_mock.update_navigation_expanded(True)
        workspace_state_mock.update_right_dock_visible(False)
        workspace_state_mock.update_window_state(1280, 800, False)

        ws_path = get_workspace_state_path()
        state, load_ok = workspace_state_mock.load_workspace_state()
        ok = (
            ws_path.is_file()
            and "verification/R035" in ws_path.as_posix()
            and load_ok
            and state["current_project"]["name"] == PROJECT_B
            and PROJECT_A in state.get("recent_projects", [])
            and PROJECT_B in state.get("recent_projects", [])
            and state.get("last_page") == "scan"
            and state.get("navigation_expanded") is True
            and state.get("right_dock_visible") is False
        )
        if ok:
            report.pass_check("workspace_project_restore", ws_path.relative_to(ROOT).as_posix())
        else:
            report.fail_check("workspace_project_restore", json.dumps(state, ensure_ascii=False)[:200])
    except Exception as exc:  # noqa: BLE001
        report.fail_check("workspace_project_restore", str(exc))


def check_page_switch_regression(report: verification_report.VerificationReport) -> None:
    report.start_check("page_switch_regression")
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        project_mock.open_project_mock(PROJECT_A)
        win._refresh_project_ui()

        sequence = (
            MainWindow.PAGE_SCAN,
            MainWindow.PAGE_DEVICE,
            MainWindow.PAGE_ANALYSIS,
            MainWindow.PAGE_REPORT,
            MainWindow.PAGE_SCAN,
        )
        ok = True
        last_crumb = ""
        for page_index in sequence:
            win._switch_page(page_index)
            _process(app)
            docks = win.findChildren(QDockWidget)
            nav_texts = [
                btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()
            ]
            dock_title = win._right_dock.windowTitle() if win._right_dock else ""
            toolbar = toolbar_texts(win)
            last_crumb = _breadcrumb_scan(win) if page_index == MainWindow.PAGE_SCAN else last_crumb
            page_ok = (
                len(docks) == 1
                and win._right_dock is not None
                and not win._right_dock.isFloating()
                and dock_title == DOCK_TITLES[page_index]
                and "项目" not in nav_texts
            )
            if page_index == MainWindow.PAGE_REPORT:
                page_ok = page_ok and all(t in toolbar for t in REPORT_TOOLBAR)
            elif page_index == MainWindow.PAGE_SCAN:
                page_ok = page_ok and all(t in toolbar for t in SCAN_TOOLBAR)
            if not page_ok:
                ok = False
                break

        ok = ok and PROJECT_A in last_crumb
        if ok:
            report.pass_check("page_switch_regression")
        else:
            report.fail_check("page_switch_regression", f"crumb={last_crumb}")
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("page_switch_regression", str(exc))


def check_no_real_device_access(report: verification_report.VerificationReport) -> None:
    report.start_check("no_real_device_access")
    hits: list[str] = []
    for base in FORBIDDEN_SCAN_PATHS:
        if not base.exists():
            continue
        paths = [base] if base.is_file() else list(base.rglob("*.py"))
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in text:
                    hits.append(f"{path.relative_to(UTILS_ROOT)}: {pattern}")
    if _runtime_export_files():
        hits.append("runtime has pdf/docx/xlsx exports")
    if hits:
        report.fail_check("no_real_device_access", "; ".join(hits[:8]))
    else:
        report.pass_check("no_real_device_access")


def check_no_high_fidelity_changes(report: verification_report.VerificationReport) -> None:
    report.start_check("no_high_fidelity_changes")
    proc = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    bad = [
        line.strip()
        for line in proc.stdout.splitlines()
        if line.strip().startswith("prototypes/high_fidelity/")
    ]
    if bad:
        report.fail_check("no_high_fidelity_changes", ", ".join(bad))
    else:
        report.pass_check("no_high_fidelity_changes")


def write_acceptance_report(report: verification_report.VerificationReport) -> Path:
    out = (
        ROOT
        / "docs/product-spec/release/Release_035_Scan_Task_Workspace_Integration/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    setup_path()
    from nfs_scanner_pro.app_paths import get_workspace_state_path

    ws_display = get_workspace_state_path()
    try:
        ws_rel = ws_display.relative_to(ROOT).as_posix()
    except ValueError:
        ws_rel = str(ws_display)
    path_a = (
        SESSION.scan_dir_a.relative_to(ROOT).as_posix()
        if SESSION.scan_dir_a
        else "（见验收运行）"
    )
    path_b = (
        SESSION.scan_dir_b.relative_to(ROOT).as_posix()
        if SESSION.scan_dir_b
        else "（见验收运行）"
    )
    lines = [
        "# Release_035 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_035.py",
        "python scripts/verify_all.py --only 035",
        "python scripts/verify_all.py",
        "```",
        "",
        "## 检查项",
        "",
    ]
    for name, ok, detail, elapsed, skipped in report.entries:
        status = "SKIP" if skipped else ("PASS" if ok else "FAIL")
        suffix = f" — {detail}" if detail else ""
        timing = f" ({elapsed:.2f}s)" if elapsed is not None else ""
        lines.append(f"- [{status}] `{name}`{timing}{suffix}")
    lines.extend(
        [
            "",
            "## 结果",
            "",
            "PASS" if report.is_pass() else "FAIL",
            "",
            "## runtime 隔离路径",
            "",
            "- `runtime/verification/R035/`",
            "",
            "## 项目 A 扫描结果路径",
            "",
            f"- `{path_a}`",
            "",
            "## 项目 B 扫描结果路径",
            "",
            f"- `{path_b}`",
            "",
            "## workspace_state_mock.json 路径",
            "",
            f"- `{ws_rel}`",
            "",
            "## 是否接真实设备",
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
            "是" if report.is_pass() else "否",
            "",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    setup_path()
    verification_runtime.enter_release_runtime("R035")
    report = verification_report.VerificationReport("035")

    check_compileall(report)
    check_runtime_isolation(report)
    check_mainwindow_boot(report)
    check_current_project_init(report)
    check_project_switch_scan_sync(report)
    check_project_a_scan_result_path(report)
    check_project_b_scan_result_path(report)
    check_scantask_config_project_binding(report)
    check_analysis_data_source_project_isolation(report)
    check_report_data_source_project_isolation(report)
    check_workspace_project_restore(report)
    check_page_switch_regression(report)
    check_no_real_device_access(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
