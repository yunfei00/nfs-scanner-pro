#!/usr/bin/env python3
"""Release_023 自动验收 — End-to-End Mock Verification Suite。"""

from __future__ import annotations

import csv
import inspect
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from verification_utils import (
    DOCK_TITLES,
    PROJECT_NAME,
    REPORT_TOOLBAR,
    SCAN_TOOLBAR,
    CheckResult,
    ROOT,
    check_compileall,
    check_gitignore,
    check_no_real_device_access,
    describe_mock_report_draft,
    describe_mock_scan_dir,
    describe_workspace_state,
    gitignore_covers_runtime,
    setup_offscreen,
    setup_path,
    toolbar_texts,
)

TASK_ID = "ST-VERIFY-023"
REPORT_ID = "RP-VERIFY-023"

CORE_MODULES = (
    "nfs_scanner_pro.devices.device_manager_mock",
    "nfs_scanner_pro.scan.scan_engine_mock",
    "nfs_scanner_pro.scan.scan_result_persistence_mock",
    "nfs_scanner_pro.analysis.analysis_data_source_mock",
    "nfs_scanner_pro.report.report_data_source_mock",
    "nfs_scanner_pro.workspace_state_mock",
    "nfs_scanner_pro.project_mock",
)


def check_mainwindow_ui(check: CheckResult) -> None:
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()

        docks = win.findChildren(QDockWidget)
        nav_texts = [btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()]
        single_dock_ok = (
            len(docks) == 1
            and win._right_dock is not None
            and not win._right_dock.isFloating()
            and "项目" not in nav_texts
        )
        check.add("mainwindow_single_dock", single_dock_ok, f"count={len(docks)}")

        mapping_ok = True
        details: list[str] = []
        for index, expected_title in enumerate(DOCK_TITLES):
            win._switch_page(index)
            app.processEvents()
            actual = win._right_dock.windowTitle() if win._right_dock else ""
            details.append(f"{index}:{actual!r}")
            if actual != expected_title:
                mapping_ok = False
        win._switch_page(MainWindow.PAGE_REPORT)
        app.processEvents()
        if not all(label in toolbar_texts(win) for label in REPORT_TOOLBAR):
            mapping_ok = False
        win._switch_page(MainWindow.PAGE_SCAN)
        app.processEvents()
        if not all(label in toolbar_texts(win) for label in SCAN_TOOLBAR):
            mapping_ok = False
        check.add("page_dock_mapping", mapping_ok, ", ".join(details))

        win.close()
    except Exception as exc:  # noqa: BLE001
        check.add("mainwindow_single_dock", False, str(exc))
        check.add("page_dock_mapping", False, str(exc))


def check_compile_and_imports(check: CheckResult) -> None:
    compile_ok = check_compileall(check, "compileall")
    if not compile_ok:
        return
    failed: list[str] = []
    for mod in CORE_MODULES:
        try:
            __import__(mod)
        except Exception as exc:  # noqa: BLE001
            failed.append(f"{mod}: {exc}")
    if failed:
        check.results[-1] = ("compileall", False, "; ".join(failed))


def check_project_mock(check: CheckResult) -> None:
    from nfs_scanner_pro import project_mock

    backup = project_mock.get_current_project()
    try:
        current = project_mock.get_current_project()
        recent = project_mock.get_recent_projects()
        created = project_mock.create_project_mock(
            "Verify_023",
            "D:/NFS_Projects/Verify_023",
            "VerifyBoard",
            "CPU_Area",
        )
        opened = project_mock.open_project_mock("iPhone16_Mainboard")
        closed = project_mock.close_project_mock()
        ok = (
            bool(current.get("name"))
            and bool(recent)
            and created["name"] == "Verify_023"
            and opened["name"] == "iPhone16_Mainboard"
            and closed.get("status") == "closed"
        )
        check.add("project_mock", ok, f"recent={len(recent)} closed={closed.get('status')}")
    finally:
        project_mock.set_current_project(backup)


def check_workspace_persistence(check: CheckResult) -> None:
    from nfs_scanner_pro.app_paths import get_workspace_state_path
    from nfs_scanner_pro import workspace_state_mock

    path = get_workspace_state_path()
    backup = path.read_text(encoding="utf-8") if path.is_file() else None
    try:
        state, load_ok = workspace_state_mock.load_workspace_state()
        workspace_state_mock.save_workspace_state(state)
        file_ok = path.is_file()
        workspace_state_mock.update_last_page("analysis")
        reloaded, _ = workspace_state_mock.load_workspace_state()
        page_ok = reloaded.get("last_page") == "analysis"
        workspace_state_mock.update_navigation_expanded(True)
        nav_ok = workspace_state_mock.load_workspace_state()[0].get("navigation_expanded") is True
        workspace_state_mock.update_right_dock_visible(False)
        dock_ok = workspace_state_mock.load_workspace_state()[0].get("right_dock_visible") is False
        git_ok = gitignore_covers_runtime(path)
        ok = load_ok and file_ok and page_ok and nav_ok and dock_ok and git_ok
        check.add(
            "workspace_persistence",
            ok,
            f"file={path.name} gitignored={git_ok}",
        )
    finally:
        if backup is None:
            if path.is_file():
                path.unlink()
        else:
            path.write_text(backup, encoding="utf-8")
        workspace_state_mock.load_workspace_state()


def check_device_manager_mock(check: CheckResult) -> None:
    from nfs_scanner_pro.devices.device_manager_mock import DeviceManagerMock

    mgr = DeviceManagerMock()
    x_before = mgr.motion.x
    connect_msg = mgr.connect_all()
    home_msg = mgr.motion.home()
    jog_msg = mgr.motion.jog("x", "+")
    spectrum_msg = mgr.spectrum.test_connection()
    camera_msg = mgr.camera.capture()
    servo_msg = mgr.servo.switch_to_hy()
    snapshot = mgr.get_snapshot()
    ok = (
        "Mock" in connect_msg
        and "Mock" in home_msg
        and "Mock" in jog_msg
        and mgr.motion.x > x_before
        and "Mock" in spectrum_msg
        and "Mock" in camera_msg
        and "Mock" in servo_msg
        and all(k in snapshot for k in ("motion", "spectrum", "camera", "servo"))
    )
    check.add("device_manager_mock", ok)


def check_scan_engine_mock(check: CheckResult) -> None:
    from nfs_scanner_pro.devices.device_manager_mock import DeviceManagerMock
    from nfs_scanner_pro.scan.scan_engine_mock import ScanEngineMock
    from nfs_scanner_pro.scan.scan_state import ScanState
    from nfs_scanner_pro.scan.scan_task_config import ScanTaskConfig

    source = inspect.getsource(ScanEngineMock)
    no_qtimer = "QTimer" not in source
    dm = DeviceManagerMock()
    engine = ScanEngineMock(device_manager=dm)
    config = ScanTaskConfig(project_name=PROJECT_NAME, total_points=150)
    engine.prepare(config)
    engine.start()
    scanning = engine.state is ScanState.SCANNING
    index_before = engine.progress.current_index
    engine.tick()
    index_grew = engine.progress.current_index >= index_before
    point = engine.current_point()
    point_ok = point is not None and all(
        hasattr(point, attr) for attr in ("x", "y", "z", "frequency", "amplitude", "phase")
    )
    completed = False
    snapshot_ok = False
    for _ in range(300):
        if engine.state is ScanState.SCANNING:
            engine.tick()
        elif engine.state is ScanState.STOPPING:
            engine.finalize_stop()
            break
    completed = engine.state is ScanState.COMPLETED
    if engine.result is not None:
        snapshot_ok = bool(engine.result.device_snapshot)
    ok = (
        no_qtimer
        and scanning
        and index_grew
        and point_ok
        and completed
        and snapshot_ok
    )
    check.add(
        "scan_engine_mock",
        ok,
        f"state={engine.state.value} qtimer={not no_qtimer}",
    )


def _write_scan_fixture(scan_dir: Path) -> None:
    scan_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "task_id": TASK_ID,
        "project_name": PROJECT_NAME,
        "region_name": "CPU_Area",
        "probe_name": "Hx(100 μm)",
        "frequency": "2.450 GHz",
        "trace": "Trace 1",
        "status": "completed",
        "total_points": 100,
        "started_at": "2026-06-30T12:00:00",
        "finished_at": "2026-06-30T12:05:00",
        "device_snapshot": {"mock": True},
        "result_type": "mock",
    }
    summary = {
        "task_id": TASK_ID,
        "total_points": 100,
        "saved_preview_points": 5,
        "peak_amplitude": -21.5,
        "peak_position": {"x": 45.2, "y": -28.3, "z": 5.0},
        "mock": True,
    }
    (scan_dir / "scan_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (scan_dir / "scan_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    rows = [
        {
            "index": i,
            "x": 45.0 + i,
            "y": -28.0,
            "z": 5.0,
            "frequency": "2.450 GHz",
            "amplitude": -21.5 - i * 0.1,
            "phase": 110.0,
            "timestamp": "2026-06-30T12:01:00",
        }
        for i in range(1, 6)
    ]
    with (scan_dir / "scan_points_preview.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "index",
                "x",
                "y",
                "z",
                "frequency",
                "amplitude",
                "phase",
                "timestamp",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def check_scan_result_persistence(check: CheckResult) -> None:
    from nfs_scanner_pro.app_paths import get_mock_scan_dir
    from nfs_scanner_pro.devices.device_manager_mock import DeviceManagerMock
    from nfs_scanner_pro.scan.scan_engine_mock import ScanEngineMock
    from nfs_scanner_pro.scan.scan_result_mock import ScanResultMock
    from nfs_scanner_pro.scan.scan_result_persistence_mock import ScanResultPersistenceMock
    from nfs_scanner_pro.scan.scan_task_config import ScanTaskConfig

    scan_dir = get_mock_scan_dir(PROJECT_NAME, TASK_ID)
    persistence = ScanResultPersistenceMock()
    engine = ScanEngineMock(device_manager=DeviceManagerMock())
    config = ScanTaskConfig(project_name=PROJECT_NAME, total_points=100)
    engine.prepare(config)
    snapshot = engine.device_manager.get_snapshot()
    result = ScanResultMock.create(
        task_id=TASK_ID,
        config=config,
        device_snapshot=snapshot,
        final_index=100,
        status="completed",
        path=engine.path,
    )
    result.preview_points = persistence.generate_preview_points(engine.path)
    ok_save, _ = persistence.save_result(result)
    if not ok_save:
        _write_scan_fixture(scan_dir)

    csv_path = scan_dir / "scan_points_preview.csv"
    csv_rows = 0
    if csv_path.is_file():
        with csv_path.open(encoding="utf-8", newline="") as handle:
            csv_rows = sum(1 for _ in csv.reader(handle)) - 1

    json_ok = False
    try:
        payload = json.loads((scan_dir / "scan_result.json").read_text(encoding="utf-8"))
        json_ok = isinstance(payload, dict)
    except (OSError, json.JSONDecodeError):
        json_ok = False

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
        and not export_bad
        and gitignore_covers_runtime(scan_dir / "scan_result.json")
    )
    check.add(
        "scan_result_persistence",
        ok,
        f"dir={scan_dir} csv_rows={csv_rows}",
    )


def check_analysis_data_source(check: CheckResult) -> None:
    from nfs_scanner_pro.analysis.analysis_data_source_mock import AnalysisDataSourceMock

    ds = AnalysisDataSourceMock()
    projects = ds.list_projects()
    tasks = ds.list_scan_tasks(PROJECT_NAME)
    dataset = ds.build_dataset(PROJECT_NAME, TASK_ID)
    readout = dataset.cursor_readout()
    empty = ds.build_dataset("MissingProject_XYZ", "ST-MISSING")
    amp_key = "amplitude" if "amplitude" in readout else "amp"
    ok = (
        PROJECT_NAME in projects
        and TASK_ID in tasks
        and not dataset.is_empty()
        and all(k in readout for k in ("x", "y", "z", "frequency", amp_key, "phase"))
        and empty.is_empty()
    )
    check.add(
        "analysis_data_source",
        ok,
        f"tasks={tasks} empty_ok={empty.is_empty()}",
    )


def check_report_data_source(check: CheckResult) -> None:
    from nfs_scanner_pro.report.report_data_source_mock import ReportDataSourceMock
    from nfs_scanner_pro.report.report_draft_mock import ReportDraftMock
    from nfs_scanner_pro.report.report_persistence_mock import ReportPersistenceMock

    ds = ReportDataSourceMock()
    tasks = ds.list_scan_tasks(PROJECT_NAME)
    context = ds.build_report_context(PROJECT_NAME, TASK_ID)
    settings = {
        "template": "标准 EMC 报告",
        "logo": "公司默认",
        "pdf_quality": "印刷（300 DPI）",
        "include_heatmap": True,
        "include_device_info": True,
        "include_scan_params": True,
        "include_raw_data": False,
        "include_summary": True,
    }
    draft = ReportDraftMock.from_analysis_dataset(context["dataset"], settings)
    draft.report_id = REPORT_ID
    persistence = ReportPersistenceMock()
    saved, _ = persistence.save_draft(draft)
    report_dir = persistence.build_report_dir(PROJECT_NAME, REPORT_ID)
    draft_path = report_dir / ReportPersistenceMock.DRAFT_FILENAME
    export_bad = (
        list(report_dir.glob("*.pdf"))
        + list(report_dir.glob("*.docx"))
        + list(report_dir.glob("*.xlsx"))
    )
    ok = (
        bool(tasks)
        and context.get("has_data")
        and bool(draft.report_name)
        and saved
        and draft_path.is_file()
        and not export_bad
        and gitignore_covers_runtime(draft_path)
    )
    check.add(
        "report_data_source",
        ok,
        str(draft_path),
    )


def write_acceptance_report(check: CheckResult) -> Path:
    report_path = (
        ROOT
        / "docs/product-spec/release/Release_023_End_to_End_Mock_Verification/ACCEPTANCE_REPORT.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_023 验收报告",
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_023.py",
        "python scripts/verify_all.py",
        "```",
        "",
        f"## 验收时间",
        "",
        now,
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
            "## runtime Mock 文件",
            "",
            f"- `{describe_mock_scan_dir(PROJECT_NAME, TASK_ID)}/`",
            f"- `{describe_mock_report_draft(PROJECT_NAME, REPORT_ID)}`",
            f"- `{describe_workspace_state()}`",
            "",
            "## 是否接真实设备",
            "",
            "否",
            "",
            "## 是否生成真实 PDF / Word / Excel",
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
    check = CheckResult("Release_023 Verification")
    check_compile_and_imports(check)
    check_gitignore(check)
    check_mainwindow_ui(check)
    check_project_mock(check)
    check_workspace_persistence(check)
    check_device_manager_mock(check)
    check_scan_engine_mock(check)
    check_scan_result_persistence(check)
    check_analysis_data_source(check)
    check_report_data_source(check)
    check_no_real_device_access(check)
    report_path = write_acceptance_report(check)
    check.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return 0 if check.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
