#!/usr/bin/env python3
"""Release_036 自动验收 — Analysis Page ScanTask Selection Integration。"""

from __future__ import annotations

import compileall
import csv
import io
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
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
    "nfs_scanner_pro.ui.pages.analysis_page",
    "nfs_scanner_pro.ui.analysis_parameter_dock",
    "nfs_scanner_pro.project_mock",
    "nfs_scanner_pro.workspace_state_mock",
    "nfs_scanner_pro.analysis.analysis_data_source_mock",
    "nfs_scanner_pro.analysis.analysis_dataset_mock",
    "nfs_scanner_pro.scan.scan_result_persistence_mock",
    "nfs_scanner_pro.app_paths",
)

PROJECT_A = "iPhone16_Mainboard"
PROJECT_B = "RF_Module_Test"
REGION_A = "CPU_Area"
REGION_B = "RF_Area"
EMPTY_PROJECT = "Empty_Project_For_R036"
TASK_A1 = "ST-R036-A-001"
TASK_A2 = "ST-R036-A-002"
TASK_B1 = "ST-R036-B-001"

FORBIDDEN_SCAN_PATHS = MOCK_DEVICE_DIRS + (
    ROOT / "src/nfs_scanner_pro/ui/dialogs",
    ROOT / "src/nfs_scanner_pro/project_mock.py",
    ROOT / "src/nfs_scanner_pro/workspace_state_mock.py",
)

EXPORT_EXTENSIONS = {".pdf", ".docx", ".xlsx"}
WORKFLOW_PAGES = (0, 1, 2, 3, 2, 0)


@dataclass
class Session:
    tasks_a: list[str] = field(default_factory=list)
    tasks_b: list[str] = field(default_factory=list)
    scan_dirs: dict[str, Path] = field(default_factory=dict)
    default_task_note: str = ""


SESSION = Session()


def _process(app, rounds: int = 10) -> None:
    for _ in range(rounds):
        app.processEvents()
        time.sleep(0.02)


def _status_text(win) -> str:
    return win._status._message.text()


def _combo_items(combo) -> list[str]:
    return [combo.itemText(i) for i in range(combo.count())]


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


def _reset_runtime(*, clean: bool = True) -> Path:
    if clean:
        verification_runtime.clean_release_runtime("036")
    runtime_dir = verification_runtime.enter_release_runtime("R036")
    setup_path()
    from nfs_scanner_pro import project_mock, workspace_state_mock
    from nfs_scanner_pro.app_paths import get_workspace_state_path

    workspace_state_mock.reset_workspace_state()
    project_mock.apply_workspace_state(
        workspace_state_mock.DEFAULT_WORKSPACE_STATE["current_project"],
        workspace_state_mock.DEFAULT_WORKSPACE_STATE["recent_projects"],
    )
    path = get_workspace_state_path()
    if path.is_file():
        path.unlink()
    return runtime_dir


def _write_scan_fixture(
    scan_dir: Path,
    *,
    task_id: str,
    project_name: str,
    region_name: str,
    frequency: str = "2.450 GHz",
    peak_amp: float = -21.5,
) -> None:
    scan_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "task_id": task_id,
        "project_name": project_name,
        "region_name": region_name,
        "probe_name": "Hx(100 μm)",
        "frequency": frequency,
        "trace": "Trace 1",
        "status": "completed",
        "total_points": 6461,
        "started_at": "2026-06-30T12:00:00",
        "finished_at": "2026-06-30T12:05:00",
        "device_snapshot": {"mock": True},
        "result_type": "mock",
    }
    summary = {
        "task_id": task_id,
        "total_points": 6461,
        "saved_preview_points": 3,
        "peak_amplitude": peak_amp,
        "peak_position": {"x": 45.2, "y": -28.3, "z": 5.0},
        "mock": True,
    }
    rows = [
        {
            "index": i,
            "x": 45.2 + i,
            "y": -28.3,
            "z": 5.0,
            "frequency": frequency,
            "amplitude": peak_amp + i * 0.1,
            "phase": 110.0 + i,
            "timestamp": f"2026-06-30T12:0{i}:00",
        }
        for i in range(1, 4)
    ]
    (scan_dir / "scan_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (scan_dir / "scan_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=["index", "x", "y", "z", "frequency", "amplitude", "phase", "timestamp"],
    )
    writer.writeheader()
    writer.writerows(rows)
    (scan_dir / "scan_points_preview.csv").write_text(buffer.getvalue(), encoding="utf-8")


def _prepare_scan_tasks() -> None:
    from nfs_scanner_pro.app_paths import get_mock_scan_dir

    fixtures = (
        (PROJECT_A, TASK_A1, REGION_A, "2.440 GHz", -22.0),
        (PROJECT_A, TASK_A2, REGION_A, "2.450 GHz", -20.5),
        (PROJECT_B, TASK_B1, REGION_B, "5.800 GHz", -19.0),
    )
    SESSION.scan_dirs.clear()
    for project, task_id, region, freq, amp in fixtures:
        scan_dir = get_mock_scan_dir(project, task_id)
        _write_scan_fixture(
            scan_dir,
            task_id=task_id,
            project_name=project,
            region_name=region,
            frequency=freq,
            peak_amp=amp,
        )
        SESSION.scan_dirs[task_id] = scan_dir
    SESSION.tasks_a = [TASK_A1, TASK_A2]
    SESSION.tasks_b = [TASK_B1]


def _boot_mainwindow(*, open_project: str | None = PROJECT_A):
    from PySide6.QtWidgets import QApplication

    from nfs_scanner_pro import project_mock
    from nfs_scanner_pro.ui.main_window import MainWindow

    if open_project:
        project_mock.open_project_mock(open_project)
    app = QApplication.instance() or QApplication([])
    win = MainWindow()
    win.show()
    _process(app, 5)
    return app, win


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
    try:
        runtime_dir = _reset_runtime()
        from nfs_scanner_pro.app_paths import get_runtime_dir, get_workspace_state_path

        active = get_runtime_dir().resolve()
        ok = (
            active == runtime_dir.resolve()
            and "verification/R036" in active.as_posix()
            and not _runtime_export_files()
        )
        after = _list_shared_mock_files()
        if after - baseline:
            ok = False
        if ok:
            report.pass_check("runtime_isolation", get_workspace_state_path().relative_to(ROOT).as_posix())
        else:
            report.fail_check("runtime_isolation", str(active))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("runtime_isolation", str(exc))


def check_prepare_multi_project_scan_tasks(report: verification_report.VerificationReport) -> None:
    report.start_check("prepare_multi_project_scan_tasks")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R036")
        _prepare_scan_tasks()
        required = (
            SESSION.scan_dirs[TASK_A1],
            SESSION.scan_dirs[TASK_A2],
            SESSION.scan_dirs[TASK_B1],
        )
        ok = all(
            (d / name).is_file()
            for d in required
            for name in ("scan_result.json", "scan_summary.json", "scan_points_preview.csv")
        )
        for task_id, scan_dir in SESSION.scan_dirs.items():
            payload = json.loads((scan_dir / "scan_result.json").read_text(encoding="utf-8"))
            if task_id.startswith("ST-R036-A") and payload.get("project_name") != PROJECT_A:
                ok = False
            if task_id == TASK_B1 and payload.get("project_name") != PROJECT_B:
                ok = False
            if "verification/R036" not in scan_dir.as_posix().replace("\\", "/"):
                ok = False
        if ok:
            report.pass_check(
                "prepare_multi_project_scan_tasks",
                f"A={SESSION.tasks_a} B={SESSION.tasks_b}",
            )
        else:
            report.fail_check("prepare_multi_project_scan_tasks", "fixture incomplete")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("prepare_multi_project_scan_tasks", str(exc))


def check_mainwindow_boot(report: verification_report.VerificationReport) -> None:
    report.start_check("mainwindow_boot")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R036")
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        app, win = _boot_mainwindow()
        docks = win.findChildren(QDockWidget)
        nav_texts = [btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()]
        ok = (
            len(docks) == 1
            and win._right_dock is not None
            and not win._right_dock.isFloating()
            and "项目" not in nav_texts
        )
        win.close()
        _process(app, 3)
        if ok:
            report.pass_check("mainwindow_boot")
        else:
            report.fail_check("mainwindow_boot", f"docks={len(docks)} nav={nav_texts}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("mainwindow_boot", str(exc))


def check_analysis_data_source_project_isolation(report: verification_report.VerificationReport) -> None:
    report.start_check("analysis_data_source_project_isolation")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R036")
        from nfs_scanner_pro.analysis.analysis_data_source_mock import AnalysisDataSourceMock

        ds = AnalysisDataSourceMock()
        projects = ds.list_projects()
        tasks_a = ds.list_scan_tasks(PROJECT_A)
        tasks_b = ds.list_scan_tasks(PROJECT_B)
        ds_a1 = ds.build_dataset(PROJECT_A, TASK_A1)
        ds_a2 = ds.build_dataset(PROJECT_A, TASK_A2)
        ds_b1 = ds.build_dataset(PROJECT_B, TASK_B1)

        ok = (
            PROJECT_A in projects
            and PROJECT_B in projects
            and tasks_a == SESSION.tasks_a
            and tasks_b == SESSION.tasks_b
            and TASK_B1 not in tasks_a
            and TASK_A1 not in tasks_b
            and TASK_A2 not in tasks_b
            and not ds_a1.is_empty()
            and not ds_a2.is_empty()
            and not ds_b1.is_empty()
            and ds_a1.project_name == PROJECT_A
            and ds_a2.project_name == PROJECT_A
            and ds_b1.project_name == PROJECT_B
            and all(
                "verification/R036" in p.replace("\\", "/")
                for p in (ds_a1.source_path, ds_a2.source_path, ds_b1.source_path)
            )
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


def check_analysis_default_load_current_project(report: verification_report.VerificationReport) -> None:
    report.start_check("analysis_default_load_current_project")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R036")
        from PySide6.QtWidgets import QLabel

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        project_mock.open_project_mock(PROJECT_A)
        app, win = _boot_mainwindow()
        win._switch_page(MainWindow.PAGE_ANALYSIS)
        _process(app, 8)

        combo = win._analysis_panel.data_source_panel._task_combo
        items = _combo_items(combo)
        selected = combo.currentText()
        crumb = win._analysis_page.findChild(QLabel, "breadcrumbBar")
        crumb_text = crumb.text() if crumb else ""
        status = _status_text(win)
        dock_title = win._right_dock.windowTitle() if win._right_dock else ""
        dataset = win._analysis_page._mock.dataset

        if selected == TASK_A2:
            SESSION.default_task_note = "default latest ST-R036-A-002"
        else:
            SESSION.default_task_note = f"default task {selected!r} (sorted last={TASK_A2})"

        ok = (
            win._current_page == MainWindow.PAGE_ANALYSIS
            and dock_title == "分析参数"
            and TASK_A1 in items
            and TASK_A2 in items
            and TASK_B1 not in items
            and selected in items
            and dataset.project_name == PROJECT_A
            and not dataset.is_empty()
            and PROJECT_A in crumb_text
            and "CPU_Area" in crumb_text
            and "ScanTask" in crumb_text
            and "Trace" in crumb_text
            and "GHz" in crumb_text
            and (
                "分析就绪" in status
                or "Mock 扫描结果" in status
                or "已加载" in status
            )
        )
        win.close()
        if ok:
            report.pass_check("analysis_default_load_current_project", SESSION.default_task_note)
        else:
            report.fail_check(
                "analysis_default_load_current_project",
                f"items={items} selected={selected} status={status!r}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("analysis_default_load_current_project", str(exc))


def check_scantask_dropdown_switching(report: verification_report.VerificationReport) -> None:
    report.start_check("scantask_dropdown_switching")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R036")
        from PySide6.QtWidgets import QLabel

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        project_mock.open_project_mock(PROJECT_A)
        app, win = _boot_mainwindow()
        win._switch_page(MainWindow.PAGE_ANALYSIS)
        _process(app, 5)

        combo = win._analysis_panel.data_source_panel._task_combo
        first = TASK_A1
        second = TASK_A2
        combo.setCurrentText(first)
        _process(app, 5)
        ds_first = win._analysis_page._mock.dataset
        status_first = _status_text(win)

        combo.setCurrentText(second)
        _process(app, 5)
        ds_second = win._analysis_page._mock.dataset
        status_second = _status_text(win)
        crumb = win._analysis_page.findChild(QLabel, "breadcrumbBar")
        crumb_text = crumb.text() if crumb else ""
        status_label = win._analysis_panel.data_source_panel._status_label.text()

        ok = (
            ds_first.task_id == first
            and ds_second.task_id == second
            and second in crumb_text
            and status_label == "已加载"
            and (
                "已加载分析数据源" in status_second
                or "分析就绪" in status_second
                or "Mock 扫描结果" in status_second
            )
            and ds_first.task_id != ds_second.task_id
        )
        win.close()
        if ok:
            report.pass_check("scantask_dropdown_switching", f"{first}->{second}")
        else:
            report.fail_check(
                "scantask_dropdown_switching",
                f"first={ds_first.task_id} second={ds_second.task_id} status={status_second!r}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("scantask_dropdown_switching", str(exc))


def check_project_switch_analysis_refresh(report: verification_report.VerificationReport) -> None:
    report.start_check("project_switch_analysis_refresh")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R036")
        from PySide6.QtWidgets import QLabel

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        project_mock.open_project_mock(PROJECT_A)
        app, win = _boot_mainwindow()
        win._switch_page(MainWindow.PAGE_ANALYSIS)
        _process(app, 5)

        project_mock.open_project_mock(PROJECT_B)
        win._refresh_project_ui()
        _process(app, 8)

        combo = win._analysis_panel.data_source_panel._task_combo
        items = _combo_items(combo)
        selected = combo.currentText()
        dataset = win._analysis_page._mock.dataset
        crumb = win._analysis_page.findChild(QLabel, "breadcrumbBar")
        crumb_text = crumb.text() if crumb else ""
        status = _status_text(win)

        ok = (
            items == [TASK_B1]
            and TASK_A1 not in items
            and TASK_A2 not in items
            and selected == TASK_B1
            and dataset.project_name == PROJECT_B
            and dataset.task_id == TASK_B1
            and PROJECT_B in crumb_text
            and (
                "分析就绪" in status
                or "Mock 扫描结果" in status
                or "已加载" in status
            )
        )
        win.close()
        if ok:
            report.pass_check("project_switch_analysis_refresh")
        else:
            report.fail_check(
                "project_switch_analysis_refresh",
                f"items={items} selected={selected} dataset={dataset.project_name}/{dataset.task_id}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("project_switch_analysis_refresh", str(exc))


def check_empty_project_state(report: verification_report.VerificationReport) -> None:
    report.start_check("empty_project_state")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R036")
        from PySide6.QtWidgets import QLabel

        from nfs_scanner_pro import project_mock, workspace_state_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        project_mock.create_project_mock(
            EMPTY_PROJECT,
            f"D:/NFS_Projects/{EMPTY_PROJECT}",
            EMPTY_PROJECT,
            "CPU_Area",
        )
        workspace_state_mock.snapshot_from_runtime(
            current_project=project_mock.get_current_project(),
            recent_projects=project_mock.get_recent_project_names(),
            last_page="scan",
            navigation_expanded=False,
            right_dock_visible=True,
            width=1600,
            height=1000,
            maximized=True,
        )
        app, win = _boot_mainwindow(open_project=None)
        win._switch_page(MainWindow.PAGE_ANALYSIS)
        _process(app, 8)

        combo = win._analysis_panel.data_source_panel._task_combo
        items = _combo_items(combo)
        status = _status_text(win)
        hint = win._analysis_panel.data_source_panel._hint_label.text()
        overlay = win._analysis_page._empty_overlay.text()
        overlay_visible = win._analysis_page._empty_overlay.isVisible()
        crumb = win._analysis_page.findChild(QLabel, "breadcrumbBar")
        crumb_text = crumb.text() if crumb else ""
        dataset = win._analysis_page._mock.dataset

        ok = (
            len(items) == 0
            and dataset.is_empty()
            and overlay_visible
            and (
                "未发现 Mock 扫描结果" in overlay
                or "未发现 Mock 扫描结果" in hint
                or "Mock 扫描" in hint
            )
            and (
                "未发现 Mock 扫描结果" in status
                or "分析就绪" in status
            )
            and TASK_A1 not in crumb_text
            and TASK_A2 not in crumb_text
            and (EMPTY_PROJECT in crumb_text or EMPTY_PROJECT in status or dataset.project_name == EMPTY_PROJECT)
        )
        win.close()
        if ok:
            report.pass_check("empty_project_state", EMPTY_PROJECT)
        else:
            report.fail_check(
                "empty_project_state",
                f"items={items} status={status!r} overlay={overlay!r}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("empty_project_state", str(exc))


def check_cursor_readout_dataset_binding(report: verification_report.VerificationReport) -> None:
    report.start_check("cursor_readout_dataset_binding")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R036")
        from nfs_scanner_pro import project_mock, workspace_state_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        project_mock.open_project_mock(PROJECT_A)
        workspace_state_mock.update_current_project(project_mock.get_current_project())
        app, win = _boot_mainwindow(open_project=None)
        win._switch_page(MainWindow.PAGE_ANALYSIS)
        _process(app, 5)

        readout = win._analysis_page._mock.dataset.cursor_readout()
        panel = win._analysis_panel.control_panel._cursor_panel
        labels = panel._labels
        amp_key = "amplitude" if "amplitude" in readout else "amp"
        values_ok = all(
            labels[k].text() not in ("", "—")
            for k in ("x", "y", "z", "frequency", "amp", "phase")
        )
        keys_ok = all(k in readout for k in ("x", "y", "z", "frequency", amp_key, "phase"))

        combo = win._analysis_panel.data_source_panel._task_combo
        combo.setCurrentText(TASK_A1)
        _process(app, 5)
        readout_a = win._analysis_page._mock.dataset.cursor_readout()
        combo.setCurrentText(TASK_A2)
        _process(app, 5)
        readout_b = win._analysis_page._mock.dataset.cursor_readout()

        panel._lock_btn.click()
        _process(app, 3)
        lock_status = _status_text(win)
        panel._lock_btn.click()
        _process(app, 3)

        copy_btn = panel.findChild(type(panel._lock_btn), "cursorCopyButton")
        copy_btn.click()
        _process(app, 3)
        copy_status = _status_text(win)

        ok = (
            keys_ok
            and values_ok
            and readout_a.get("frequency") != readout_b.get("frequency")
            and win._analysis_page._mock.dataset.task_id == TASK_A2
            and ("锁定" in lock_status or "光标" in lock_status)
            and ("复制" in copy_status or "读数" in copy_status)
        )
        final_task = win._analysis_page._mock.dataset.task_id
        win.close()
        if ok:
            report.pass_check("cursor_readout_dataset_binding")
        else:
            report.fail_check(
                "cursor_readout_dataset_binding",
                f"task={final_task}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("cursor_readout_dataset_binding", str(exc))


def check_trace_frequency_lut_controls(report: verification_report.VerificationReport) -> None:
    report.start_check("trace_frequency_lut_controls")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R036")
        from PySide6.QtWidgets import QLabel

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        project_mock.open_project_mock(PROJECT_A)
        app, win = _boot_mainwindow()
        win._switch_page(MainWindow.PAGE_ANALYSIS)
        _process(app, 5)

        control = win._analysis_panel.control_panel
        crumb = win._analysis_page.findChild(QLabel, "breadcrumbBar")
        statuses: list[str] = []

        def snap() -> None:
            _process(app, 3)
            statuses.append(_status_text(win))

        trace_target = "Trace 2" if control._trace_combo.currentText() == "Trace 1" else "Trace 1"
        control._trace_combo.setCurrentText(trace_target)
        snap()

        freqs = [control._freq_combo.itemText(i) for i in range(control._freq_combo.count())]
        freq_target = freqs[1] if len(freqs) > 1 else freqs[0]
        control._freq_combo.setCurrentText(freq_target)
        snap()

        lut_target = "Jet" if control._lut_selector.currentText() != "Jet" else "Turbo"
        control._lut_selector.setCurrentText(lut_target)
        snap()

        control._opacity_slider.setValue(max(10, control._opacity_slider.value() - 5))
        snap()

        crumb_text = crumb.text() if crumb else ""
        ok = (
            trace_target in crumb_text
            and freq_target in crumb_text
            and any("分析参数" in s or "LUT" in s or "分析就绪" in s for s in statuses)
        )
        win.close()
        if ok:
            report.pass_check("trace_frequency_lut_controls")
        else:
            report.fail_check("trace_frequency_lut_controls", f"crumb={crumb_text!r}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("trace_frequency_lut_controls", str(exc))


def check_page_switch_regression(report: verification_report.VerificationReport) -> None:
    report.start_check("page_switch_regression")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R036")
        from PySide6.QtWidgets import QDockWidget, QToolButton

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        project_mock.open_project_mock(PROJECT_B)
        app, win = _boot_mainwindow(open_project=None)
        failures: list[str] = []

        for page_index in WORKFLOW_PAGES:
            win._switch_page(page_index)
            _process(app, 4)
            dock_title = win._right_dock.windowTitle() if win._right_dock else ""
            if dock_title != DOCK_TITLES[page_index]:
                failures.append(f"page={page_index} dock={dock_title!r}")
            toolbar = toolbar_texts(win)
            if page_index == MainWindow.PAGE_REPORT:
                if not all(t in toolbar for t in REPORT_TOOLBAR):
                    failures.append(f"page={page_index} toolbar={toolbar}")
            elif not all(t in toolbar for t in SCAN_TOOLBAR):
                failures.append(f"page={page_index} toolbar={toolbar}")

        docks = win.findChildren(QDockWidget)
        nav_texts = [btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()]
        if len(docks) != 1:
            failures.append(f"docks={len(docks)}")
        if win._right_dock is not None and win._right_dock.isFloating():
            failures.append("dock floating")
        if "项目" in nav_texts:
            failures.append("nav has 项目")

        win.close()
        if failures:
            report.fail_check("page_switch_regression", "; ".join(failures))
        else:
            report.pass_check("page_switch_regression")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("page_switch_regression", str(exc))


def check_workspace_state_saved(report: verification_report.VerificationReport) -> None:
    report.start_check("workspace_state_saved")
    try:
        setup_path()
        verification_runtime.enter_release_runtime("R036")
        from nfs_scanner_pro import project_mock, workspace_state_mock
        from nfs_scanner_pro.app_paths import get_workspace_state_path

        project_mock.open_project_mock(PROJECT_B)
        workspace_state_mock.snapshot_from_runtime(
            current_project=project_mock.get_current_project(),
            recent_projects=project_mock.get_recent_project_names(),
            last_page="analysis",
            navigation_expanded=True,
            right_dock_visible=True,
            width=1600,
            height=1000,
            maximized=True,
        )
        path = get_workspace_state_path()
        payload = json.loads(path.read_text(encoding="utf-8"))
        project_mock.open_project_mock(PROJECT_A)
        loaded, load_ok = workspace_state_mock.load_workspace_state()
        project_mock.apply_workspace_state(
            loaded["current_project"],
            loaded.get("recent_projects", []),
        )
        current = project_mock.get_current_project()

        ok = (
            load_ok
            and path.is_file()
            and "verification/R036" in path.as_posix().replace("\\", "/")
            and payload.get("last_page") == "analysis"
            and current.get("name") == PROJECT_B
            and PROJECT_A in loaded.get("recent_projects", [])
            and PROJECT_B in loaded.get("recent_projects", [])
        )
        if ok:
            report.pass_check("workspace_state_saved", path.relative_to(ROOT).as_posix())
        else:
            report.fail_check(
                "workspace_state_saved",
                f"name={current.get('name')} last_page={payload.get('last_page')}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("workspace_state_saved", str(exc))


def check_no_real_device_access(report: verification_report.VerificationReport) -> None:
    report.start_check("no_real_device_access")
    hits: list[str] = []
    for base in FORBIDDEN_SCAN_PATHS:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in text:
                    hits.append(f"{path.relative_to(UTILS_ROOT)}: {pattern}")
    if _runtime_export_files():
        hits.append("runtime export files found")
    if hits:
        report.fail_check("no_real_device_access", "; ".join(hits[:5]))
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
        / "docs/product-spec/release/Release_036_Analysis_Page_ScanTask_Selection_Integration/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_036 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_036.py",
        "python scripts/verify_all.py --only 036",
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
            "- `runtime/verification/R036/`",
            "",
            "## 项目 A ScanTask 列表",
            "",
            f"- `{TASK_A1}`",
            f"- `{TASK_A2}`",
            "",
            "## 项目 B ScanTask 列表",
            "",
            f"- `{TASK_B1}`",
            "",
            "## 空项目状态",
            "",
            f"- `{EMPTY_PROJECT}` — 分析页空状态通过",
            "",
            "## workspace_state_mock.json 路径",
            "",
            "- `runtime/verification/R036/workspace_state_mock.json`",
            "",
            "## 默认 ScanTask 说明",
            "",
            SESSION.default_task_note or "默认加载当前项目最新任务（sorted last）",
            "",
            "## 是否接真实设备",
            "",
            "否",
            "",
            "## 是否实现真实分析算法",
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
    verification_runtime.enter_release_runtime("R036")
    report = verification_report.VerificationReport("036")

    check_compileall(report)
    check_runtime_isolation(report)
    check_prepare_multi_project_scan_tasks(report)
    check_mainwindow_boot(report)
    check_analysis_data_source_project_isolation(report)
    check_analysis_default_load_current_project(report)
    check_scantask_dropdown_switching(report)
    check_project_switch_analysis_refresh(report)
    check_cursor_readout_dataset_binding(report)
    check_empty_project_state(report)
    check_trace_frequency_lut_controls(report)
    check_page_switch_regression(report)
    check_workspace_state_saved(report)
    check_no_real_device_access(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
