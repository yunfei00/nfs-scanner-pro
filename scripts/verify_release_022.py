#!/usr/bin/env python3
"""Release_022 自动验收 — Report Data Source Mock。"""

from __future__ import annotations

import compileall
import csv
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

PROJECT_NAME = "iPhone16_Mainboard"
VERIFY_TASK_ID = "ST-VERIFY-001"
VERIFY_REPORT_PREFIX = "RP-VERIFY"

FORBIDDEN_PATTERNS = (
    "serial.Serial",
    "pyvisa",
    "cv2.VideoCapture",
    "socket.create_connection",
    "subprocess.Popen",
    "os.startfile",
)

SCAN_RELATED_FILES = (
    ROOT / "src/nfs_scanner_pro/report",
    ROOT / "src/nfs_scanner_pro/analysis",
    ROOT / "src/nfs_scanner_pro/scan/scan_result_persistence_mock.py",
    ROOT / "src/nfs_scanner_pro/scan/scan_result_serializer.py",
)

GITIGNORE_REQUIRED = (
    "__pycache__/",
    "*.pyc",
    "runtime/",
    "runtime/**/*.json",
    "runtime/**/*.csv",
)

SCAN_TOOLBAR = ("开始扫描", "停止扫描", "拍照", "区域对齐", "网格", "测量")
REPORT_TOOLBAR = ("新建报告", "预览", "导出 PDF", "导出 Word", "导出 Excel")
DOCK_TITLES = ("扫描参数", "设备配置", "分析参数", "报告设置")
NAV_LABELS = ("扫描", "设备", "分析", "报告")


class CheckResult:
    def __init__(self) -> None:
        self.results: list[tuple[str, bool, str]] = []

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.results.append((name, ok, detail))

    @property
    def passed(self) -> bool:
        return all(ok for _, ok, _ in self.results)

    def print_report(self) -> None:
        def safe(text: str) -> str:
            return text.encode(sys.stdout.encoding or "utf-8", errors="backslashreplace").decode(
                sys.stdout.encoding or "utf-8",
                errors="backslashreplace",
            )

        print("Release_022 Verification\n")
        for name, ok, detail in self.results:
            status = "PASS" if ok else "FAIL"
            line = f"[{status}] {name}"
            if detail:
                line += f" — {detail}"
            print(safe(line))
        print()
        if self.passed:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")
            print("\nFailures:")
            for name, ok, detail in self.results:
                if not ok:
                    print(f"  - {name}: {detail or 'failed'}")


def _mock_scan_dir(project: str, task_id: str) -> Path:
    from nfs_scanner_pro.app_paths import get_mock_scan_dir

    return get_mock_scan_dir(project, task_id)


def _has_any_scan_results() -> bool:
    runtime = ROOT / "runtime" / "mock_projects"
    if not runtime.is_dir():
        return False
    for project_dir in runtime.iterdir():
        if not project_dir.is_dir():
            continue
        scans = project_dir / "scans"
        if scans.is_dir() and any(scans.iterdir()):
            return True
    return False


def _write_minimal_scan_result(scan_dir: Path) -> None:
    scan_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "task_id": VERIFY_TASK_ID,
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
        "task_id": VERIFY_TASK_ID,
        "total_points": 100,
        "saved_preview_points": 3,
        "peak_amplitude": -21.5,
        "peak_position": {"x": 45.2, "y": -28.3, "z": 5.0},
        "mock": True,
    }
    preview_rows = [
        {
            "index": 1,
            "x": 45.2,
            "y": -28.3,
            "z": 5.0,
            "frequency": "2.450 GHz",
            "amplitude": -21.5,
            "phase": 110.0,
            "timestamp": "2026-06-30T12:01:00",
        },
        {
            "index": 2,
            "x": 46.0,
            "y": -27.5,
            "z": 5.0,
            "frequency": "2.450 GHz",
            "amplitude": -22.0,
            "phase": 111.0,
            "timestamp": "2026-06-30T12:02:00",
        },
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
    writer.writerows(preview_rows)
    (scan_dir / "scan_points_preview.csv").write_text(buffer.getvalue(), encoding="utf-8")


def ensure_mock_scan_result(check: CheckResult) -> str:
    scan_dir = _mock_scan_dir(PROJECT_NAME, VERIFY_TASK_ID)
    created = False
    if not _has_any_scan_results():
        _write_minimal_scan_result(scan_dir)
        created = True
    elif not (scan_dir / "scan_summary.json").is_file():
        _write_minimal_scan_result(scan_dir)
        created = True

    required = (
        scan_dir / "scan_result.json",
        scan_dir / "scan_summary.json",
        scan_dir / "scan_points_preview.csv",
    )
    task_id = VERIFY_TASK_ID
    if not all(path.is_file() for path in required):
        from nfs_scanner_pro.scan.scan_result_persistence_mock import (
            ScanResultPersistenceMock,
        )

        persistence = ScanResultPersistenceMock()
        tasks = persistence.list_scan_tasks(PROJECT_NAME)
        if tasks:
            task_id = tasks[0]
            scan_dir = _mock_scan_dir(PROJECT_NAME, task_id)
        else:
            _write_minimal_scan_result(scan_dir)
            created = True

    ok = all(
        (_mock_scan_dir(PROJECT_NAME, task_id) / name).is_file()
        for name in (
            "scan_result.json",
            "scan_summary.json",
            "scan_points_preview.csv",
        )
    )
    detail = str(_mock_scan_dir(PROJECT_NAME, task_id))
    if created:
        detail += " (auto-created)"
    check.add("mock_scan_result_ready", ok, detail)
    return task_id


def check_compileall(check: CheckResult) -> None:
    ok = compileall.compile_dir(
        str(SRC / "nfs_scanner_pro"),
        quiet=1,
    )
    check.add("compileall", bool(ok))


def check_imports(check: CheckResult) -> None:
    modules = (
        "nfs_scanner_pro.report.report_data_source_mock",
        "nfs_scanner_pro.report.report_draft_mock",
        "nfs_scanner_pro.report.report_preview_model",
        "nfs_scanner_pro.report.report_persistence_mock",
        "nfs_scanner_pro.analysis.analysis_data_source_mock",
        "nfs_scanner_pro.scan.scan_result_persistence_mock",
    )
    failed: list[str] = []
    for mod in modules:
        try:
            __import__(mod)
        except Exception as exc:  # noqa: BLE001
            failed.append(f"{mod}: {exc}")
    check.add("module_imports", not failed, "; ".join(failed))


def check_gitignore(check: CheckResult) -> None:
    gitignore_path = ROOT / ".gitignore"
    text = gitignore_path.read_text(encoding="utf-8") if gitignore_path.is_file() else ""
    missing = [rule for rule in GITIGNORE_REQUIRED if rule not in text]
    check.add("gitignore_runtime", not missing, ", ".join(missing) if missing else "ok")


def check_analysis_dataset(check: CheckResult, task_id: str) -> None:
    from nfs_scanner_pro.analysis.analysis_data_source_mock import AnalysisDataSourceMock

    ds = AnalysisDataSourceMock()
    projects = ds.list_projects()
    tasks = ds.list_scan_tasks(PROJECT_NAME)
    dataset = ds.build_dataset(PROJECT_NAME, task_id)
    readout = dataset.cursor_readout()

    ok = (
        PROJECT_NAME in projects
        and bool(tasks)
        and task_id in tasks
        and not dataset.is_empty()
    )
    check.add(
        "analysis_dataset_load",
        ok,
        f"projects={len(projects)} tasks={tasks} empty={dataset.is_empty()}",
    )

    amp_key = "amplitude" if "amplitude" in readout else "amp"
    keys_ok = all(k in readout for k in ("x", "y", "z", "frequency", amp_key, "phase"))
    check.add(
        "analysis_cursor_readout",
        keys_ok,
        f"keys={sorted(readout.keys())}",
    )


def check_report_data_source(check: CheckResult, task_id: str) -> None:
    from nfs_scanner_pro.report.report_data_source_mock import ReportDataSourceMock

    ds = ReportDataSourceMock()
    projects = ds.list_projects()
    tasks = ds.list_scan_tasks(PROJECT_NAME)
    context = ds.build_report_context(PROJECT_NAME, task_id)
    name = ds.default_report_name(
        PROJECT_NAME,
        "CPU_Area",
        "Hx(100 μm)",
        "2.450 GHz",
    )

    ok = (
        bool(projects)
        and bool(tasks)
        and context.get("has_data")
        and bool(name)
        and "报告" in name
    )
    check.add(
        "report_context_build",
        ok,
        f"default_name={name!r} has_data={context.get('has_data')}",
    )


def check_report_draft_and_persistence(check: CheckResult, task_id: str) -> tuple[str, Path]:
    from nfs_scanner_pro.report.report_data_source_mock import ReportDataSourceMock
    from nfs_scanner_pro.report.report_draft_mock import ReportDraftMock
    from nfs_scanner_pro.report.report_persistence_mock import ReportPersistenceMock

    ds = ReportDataSourceMock()
    context = ds.build_report_context(PROJECT_NAME, task_id)
    dataset = context["dataset"]
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
    draft = ReportDraftMock.from_analysis_dataset(dataset, settings)
    draft.report_id = f"{VERIFY_REPORT_PREFIX}-022"

    draft_ok = all(
        [
            bool(draft.report_name),
            draft.project_name == PROJECT_NAME or draft.project_name == dataset.project_name,
            draft.region_name == "CPU_Area",
            "GHz" in draft.frequency,
            bool(draft.summary),
        ]
    )
    serializable = True
    try:
        json.dumps(draft.to_dict(), ensure_ascii=False)
    except (TypeError, ValueError):
        serializable = False
    check.add(
        "report_draft_fields",
        draft_ok and serializable,
        draft.report_name,
    )

    persistence = ReportPersistenceMock()
    saved, path_or_err = persistence.save_draft(draft)
    report_dir = persistence.build_report_dir(PROJECT_NAME, draft.report_id)
    draft_path = report_dir / ReportPersistenceMock.DRAFT_FILENAME

    load_ok = draft_path.is_file()
    payload: dict = {}
    if load_ok:
        payload = json.loads(draft_path.read_text(encoding="utf-8"))

    save_ok = saved and load_ok and all(
        payload.get(k)
        for k in ("report_name", "project_name", "scan_task_id")
    )
    check.add(
        "report_draft_save",
        save_ok,
        str(draft_path) if save_ok else path_or_err,
    )

    export_bad = list(report_dir.glob("*.pdf")) + list(report_dir.glob("*.docx")) + list(
        report_dir.glob("*.xlsx")
    )
    check.add(
        "no_real_export_files",
        saved and not export_bad,
        f"unexpected={[p.name for p in export_bad]}",
    )
    return draft.report_id, report_dir


def _iter_source_files() -> list[Path]:
    files: list[Path] = []
    for item in SCAN_RELATED_FILES:
        if item.is_dir():
            files.extend(item.rglob("*.py"))
        elif item.is_file():
            files.append(item)
    return files


def check_no_real_device_access(check: CheckResult) -> None:
    hits: list[str] = []
    for path in _iter_source_files():
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                hits.append(f"{path.relative_to(ROOT)}: {pattern}")
    check.add("no_real_device_access", not hits, "; ".join(hits))


def _toolbar_texts(main_window) -> list[str]:
    from PySide6.QtWidgets import QToolButton

    buttons = main_window._tool_bar.findChildren(QToolButton)
    return [btn.text() for btn in buttons if btn.text()]


def check_mainwindow_ui(check: CheckResult) -> None:
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        app = QApplication.instance() or QApplication([])
        from nfs_scanner_pro.ui.main_window import MainWindow

        win = MainWindow()
        win.show()

        docks = win.findChildren(QDockWidget)
        dock_ok = len(docks) == 1
        check.add("mainwindow_single_right_dock", dock_ok, f"count={len(docks)}")

        nav_texts = [btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()]
        nav_ok = "项目" not in nav_texts and all(label in nav_texts for label in NAV_LABELS)
        check.add(
            "no_project_in_left_nav",
            nav_ok,
            f"nav={nav_texts}",
        )

        dock_map_ok = True
        dock_details: list[str] = []
        for index, expected_title in enumerate(DOCK_TITLES):
            win._switch_page(index)
            app.processEvents()
            actual = win._right_dock.windowTitle() if win._right_dock else ""
            dock_details.append(f"{index}:{actual!r}")
            if actual != expected_title:
                dock_map_ok = False
        check.add("page_dock_mapping", dock_map_ok, ", ".join(dock_details))

        win._switch_page(MainWindow.PAGE_REPORT)
        app.processEvents()
        report_texts = _toolbar_texts(win)
        report_ok = all(label in report_texts for label in REPORT_TOOLBAR)
        check.add("report_toolbar", report_ok, str(report_texts))

        win._switch_page(MainWindow.PAGE_SCAN)
        app.processEvents()
        scan_texts = _toolbar_texts(win)
        scan_ok = all(label in scan_texts for label in SCAN_TOOLBAR)
        check.add("scan_toolbar_restore", scan_ok, str(scan_texts))

        win.close()
    except Exception as exc:  # noqa: BLE001
        check.add("mainwindow_ui", False, str(exc))


def write_acceptance_report(
    check: CheckResult,
    task_id: str,
    report_dir: Path | None,
) -> Path:
    report_path = (
        ROOT
        / "docs/product-spec/release/Release_022_Report_Data_Source_Mock/ACCEPTANCE_REPORT.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_022 验收报告",
        "",
        f"## 验收时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_022.py",
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
            "## runtime Mock 文件",
            "",
            f"- 扫描：`runtime/mock_projects/{PROJECT_NAME}/scans/{task_id}/`",
        ]
    )
    if report_dir is not None:
        lines.append(f"- 报告草稿：`{report_dir.as_posix()}/report_draft.json`")
    lines.extend(
        [
            "",
            "## 是否生成真实 PDF / Word / Excel",
            "",
            "否",
            "",
            "## 是否接真实设备",
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
    check = CheckResult()
    check_compileall(check)
    check_imports(check)
    check_gitignore(check)
    task_id = ensure_mock_scan_result(check)
    check_analysis_dataset(check, task_id)
    check_report_data_source(check, task_id)
    report_id, report_dir = check_report_draft_and_persistence(check, task_id)
    del report_id
    check_no_real_device_access(check)
    check_mainwindow_ui(check)

    report_path = write_acceptance_report(check, task_id, report_dir)
    check.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return 0 if check.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
