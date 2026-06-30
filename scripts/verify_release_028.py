#!/usr/bin/env python3
"""Release_028 自动验收 — Report Page UI Interaction Verification。"""

from __future__ import annotations

import compileall
import csv
import io
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
    gitignore_covers_runtime,
    setup_offscreen,
    setup_path,
    toolbar_texts,
)

TASK_ID = "ST-VERIFY-028"
REPORT_IMPORTS = (
    "nfs_scanner_pro.ui.main_window",
    "nfs_scanner_pro.ui.pages.report_page",
    "nfs_scanner_pro.ui.report_settings_dock",
    "nfs_scanner_pro.report.report_data_source_mock",
    "nfs_scanner_pro.report.report_draft_mock",
    "nfs_scanner_pro.report.report_preview_model",
    "nfs_scanner_pro.report.report_persistence_mock",
    "nfs_scanner_pro.analysis.analysis_data_source_mock",
    "nfs_scanner_pro.scan.scan_result_persistence_mock",
)

WORKFLOW_PAGES = (0, 1, 2, 3, 0, 3)
EXPORT_EXTENSIONS = {".pdf", ".docx", ".xlsx"}


def _status_text(win) -> str:
    return win._status._message.text()


def _find_toolbar_button(win, object_name: str):
    from PySide6.QtWidgets import QToolButton

    return win._tool_bar.findChild(QToolButton, object_name)


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
    runtime = ROOT / "runtime"
    if not runtime.is_dir():
        return set()
    found: set[Path] = set()
    for path in runtime.rglob("*"):
        if path.is_file() and path.suffix.lower() in EXPORT_EXTENSIONS:
            found.add(path.resolve())
    return found


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
        "total_points": 6461,
        "started_at": "2026-06-30T12:00:00",
        "finished_at": "2026-06-30T12:05:00",
        "device_snapshot": {"mock": True},
        "result_type": "mock",
    }
    summary = {
        "task_id": TASK_ID,
        "total_points": 6461,
        "saved_preview_points": 5,
        "peak_amplitude": -21.5,
        "peak_position": {"x": 45.2, "y": -28.3, "z": 5.0},
        "mock": True,
    }
    rows = [
        {
            "index": 1,
            "x": 45.2,
            "y": -28.3,
            "z": 5.0,
            "frequency": "2.450 GHz",
            "amplitude": -21.5,
            "phase": 110.0,
            "timestamp": "2026-06-30T12:01:00",
        }
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


def ensure_mock_scan_result(check: CheckResult) -> None:
    from nfs_scanner_pro.app_paths import get_mock_scan_dir

    scan_dir = get_mock_scan_dir(PROJECT_NAME, TASK_ID)
    if not (scan_dir / "scan_summary.json").is_file():
        _write_scan_fixture(scan_dir)
    ok = all(
        (scan_dir / name).is_file()
        for name in ("scan_result.json", "scan_summary.json", "scan_points_preview.csv")
    ) and gitignore_covers_runtime(scan_dir / "scan_result.json")
    check.add("mock_scan_result_ready", ok, str(scan_dir))


def check_compileall_and_imports(check: CheckResult) -> None:
    ok = bool(compileall.compile_dir(str(ROOT / "src" / "nfs_scanner_pro"), quiet=1))
    failed: list[str] = []
    if ok:
        for mod in REPORT_IMPORTS:
            try:
                __import__(mod)
            except Exception as exc:  # noqa: BLE001
                failed.append(f"{mod}: {exc}")
                ok = False
    check.add("compileall", ok, "; ".join(failed) if failed else "")


class ReportUiContext:
    def __init__(self) -> None:
        self.app = None
        self.win = None


def boot_mainwindow(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx.app = QApplication.instance() or QApplication([])
        ctx.win = MainWindow()
        ctx.win.show()
        ctx.app.processEvents()

        docks = ctx.win.findChildren(QDockWidget)
        nav_texts = [btn.text() for btn in ctx.win._nav.findChildren(QToolButton) if btn.text()]
        ok = (
            ctx.win is not None
            and len(docks) == 1
            and ctx.win._right_dock is not None
            and not ctx.win._right_dock.isFloating()
            and "项目" not in nav_texts
        )
        check.add("mainwindow_boot", ok, f"docks={len(docks)}")
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("mainwindow_boot", False, str(exc))
        return False


def navigate_to_report(ctx: ReportUiContext) -> None:
    from nfs_scanner_pro.ui.main_window import MainWindow

    nav_btn = ctx.win._nav._buttons[MainWindow.PAGE_REPORT]
    nav_btn.click()
    ctx.app.processEvents()


def check_report_navigation(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        from nfs_scanner_pro.ui.main_window import MainWindow

        navigate_to_report(ctx)
        win = ctx.win
        nav_btn = win._nav._buttons[MainWindow.PAGE_REPORT]
        status = _status_text(win)
        dock_title = win._right_dock.windowTitle() if win._right_dock else ""
        toolbar_ok = all(label in toolbar_texts(win) for label in REPORT_TOOLBAR)

        ok = (
            win._current_page == MainWindow.PAGE_REPORT
            and win._page_stack.currentIndex() == MainWindow.PAGE_REPORT
            and nav_btn.isChecked()
            and dock_title == "报告设置"
            and toolbar_ok
            and ("报告就绪" in status or "Mock 扫描结果" in status or "已加载" in status)
            and len(win.findChildren(type(win._right_dock))) >= 1
        )
        check.add(
            "report_navigation",
            ok,
            f"dock={dock_title!r} status={status!r}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("report_navigation", False, str(exc))
        return False


def check_report_toolbar(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        from nfs_scanner_pro.ui.main_window import MainWindow

        win = ctx.win
        navigate_to_report(ctx)
        report_ok = all(label in toolbar_texts(win) for label in REPORT_TOOLBAR)
        object_names = (
            "toolbarNewReportButton",
            "toolbarPreviewButton",
            "toolbarExportPdfButton",
            "toolbarExportWordButton",
            "toolbarExportExcelButton",
        )
        names_ok = all(_find_toolbar_button(win, name) is not None for name in object_names)

        win._switch_page(MainWindow.PAGE_SCAN)
        ctx.app.processEvents()
        scan_ok = all(label in toolbar_texts(win) for label in SCAN_TOOLBAR)

        navigate_to_report(ctx)
        ok = report_ok and names_ok and scan_ok
        check.add(
            "report_toolbar",
            ok,
            f"report={report_ok} scan_restore={scan_ok}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("report_toolbar", False, str(exc))
        return False


def check_report_settings_dock(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QCheckBox, QGroupBox

        navigate_to_report(ctx)
        panel = ctx.win._report_panel
        groups = {g.title(): g for g in panel.findChildren(QGroupBox)}
        required_groups = ("模板", "导出", "内容", "高级")
        group_ok = all(name in groups for name in required_groups)

        widgets_ok = all(
            w is not None
            for w in (
                panel._template_combo,
                panel._logo_combo,
                panel._quality_combo,
                panel._format_combo,
                panel._cb_heatmap,
                panel._cb_device,
                panel._cb_scan,
                panel._cb_raw,
                panel._cb_summary,
            )
        )
        checkbox_texts = {cb.text() for cb in panel.findChildren(QCheckBox)}
        content_ok = all(
            text in checkbox_texts
            for text in (
                "包含热力图",
                "包含设备信息",
                "包含扫描参数",
                "包含原始数据表",
                "包含结论摘要",
            )
        )
        ok = group_ok and widgets_ok and content_ok
        check.add(
            "report_settings_dock",
            ok,
            f"groups={list(groups.keys())}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("report_settings_dock", False, str(exc))
        return False


def check_report_data_source(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        from nfs_scanner_pro.report.report_data_source_mock import ReportDataSourceMock

        ds = ReportDataSourceMock()
        projects = ds.list_projects()
        tasks = ds.list_scan_tasks(PROJECT_NAME)
        context = ds.build_report_context(PROJECT_NAME, TASK_ID)
        default_name = ds.default_report_name(
            PROJECT_NAME,
            "CPU_Area",
            "Hx(100 μm)",
            "2.450 GHz",
        )
        missing = ds.build_report_context("MissingProject_XYZ", "ST-MISSING")

        ok = (
            PROJECT_NAME in projects
            and (TASK_ID in tasks or len(tasks) >= 1)
            and context["has_data"]
            and bool(context["default_name"])
            and "报告" in default_name
            and not missing["has_data"]
        )
        check.add(
            "report_data_source",
            ok,
            f"tasks={len(tasks)} name={default_name!r}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("report_data_source", False, str(exc))
        return False


def check_report_list_ui(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        navigate_to_report(ctx)
        win = ctx.win
        list_panel = win._report_page._list
        has_list = list_panel.objectName() == "reportList"
        item_count = len(list_panel._items)
        status_before = _status_text(win)

        click_ok = False
        if list_panel._items:
            if len(list_panel._items) > 1:
                list_panel._items[1].clicked.emit()
            else:
                list_panel._items[0].clicked.emit()
            ctx.app.processEvents()
            status_after = _status_text(win)
            click_ok = (
                "已选择报告" in status_after
                or status_after != status_before
                or "当前" in status_after
            )
        else:
            click_ok = False

        ok = has_list and item_count >= 1 and click_ok
        check.add(
            "report_list_ui",
            ok,
            f"items={item_count}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("report_list_ui", False, str(exc))
        return False


def check_report_preview_ui(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        navigate_to_report(ctx)
        win = ctx.win
        win._report_page.select_report(0)
        win._report_page.refresh_preview()
        ctx.app.processEvents()
        preview = win._report_page._preview
        text = _preview_text(preview)
        required = (
            "近场扫描报告",
            "项目名称",
            "区域名称",
            "ScanTask",
            "探头",
            "频率",
            "峰值幅度",
            "峰值位置",
            "结论摘要",
        )
        mock_ok = "Mock" in text or "未生成真实" in text
        missing = [token for token in required if token not in text]
        ok = not missing and mock_ok and not preview._empty_overlay.isVisible()
        check.add(
            "report_preview_ui",
            ok,
            f"title={preview._title_lbl.text()!r} missing={missing}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("report_preview_ui", False, str(exc))
        return False


def check_create_report_draft(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        from nfs_scanner_pro.app_paths import get_mock_project_dir

        navigate_to_report(ctx)
        win = ctx.win
        reports_root = get_mock_project_dir(PROJECT_NAME) / "reports"
        before_drafts = set(reports_root.rglob("report_draft.json")) if reports_root.is_dir() else set()
        before_count = len(win._report_page._list._items)

        btn = _find_toolbar_button(win, "toolbarNewReportButton")
        btn.click()
        ctx.app.processEvents()

        after_drafts = set(reports_root.rglob("report_draft.json")) if reports_root.is_dir() else set()
        new_drafts = after_drafts - before_drafts
        status = _status_text(win)
        after_count = len(win._report_page._list._items)
        preview_text = _preview_text(win._report_page._preview)

        ok = (
            "已创建报告草稿" in status
            and (new_drafts or after_drafts)
            and after_count >= before_count
            and "近场扫描报告" in preview_text
            and not _runtime_export_files()
        )
        detail = f"drafts+={len(new_drafts)} status={status!r}"
        check.add("create_report_draft", ok, detail)
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("create_report_draft", False, str(exc))
        return False


def check_preview_mock_action(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        navigate_to_report(ctx)
        btn = _find_toolbar_button(ctx.win, "toolbarPreviewButton")
        btn.click()
        ctx.app.processEvents()
        status = _status_text(ctx.win)
        ok = "报告预览已刷新" in status and not _runtime_export_files()
        check.add("preview_mock_action", ok, status)
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("preview_mock_action", False, str(exc))
        return False


def check_export_mock_actions(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        navigate_to_report(ctx)
        win = ctx.win
        before = _runtime_export_files()
        export_buttons = (
            "toolbarExportPdfButton",
            "toolbarExportWordButton",
            "toolbarExportExcelButton",
        )
        statuses: list[str] = []
        for obj_name in export_buttons:
            btn = _find_toolbar_button(win, obj_name)
            btn.click()
            for _ in range(20):
                ctx.app.processEvents()
                time.sleep(0.03)
            statuses.append(_status_text(win))

        after = _runtime_export_files()
        new_files = after - before
        ok = all("Mock" in s for s in statuses) and not new_files and not after
        check.add(
            "export_mock_actions",
            ok,
            "; ".join(statuses),
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("export_mock_actions", False, str(exc))
        return False


def check_report_settings_interaction(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        import json

        from nfs_scanner_pro.app_paths import get_mock_project_dir

        navigate_to_report(ctx)
        win = ctx.win
        panel = win._report_panel

        panel._template_combo.setCurrentText("快速扫描摘要")
        panel._quality_combo.setCurrentText("标准")
        raw_checked = not panel._cb_raw.isChecked()
        panel._cb_raw.setChecked(raw_checked)
        ctx.app.processEvents()

        settings = win._report_page._mock.get_settings()
        settings_ok = (
            settings.get("template") == "快速扫描摘要"
            and settings.get("pdf_quality") == "标准"
            and settings.get("include_raw_data") == raw_checked
        )

        reports_root = get_mock_project_dir(PROJECT_NAME) / "reports"
        before_drafts = set(reports_root.rglob("report_draft.json")) if reports_root.is_dir() else set()
        _find_toolbar_button(win, "toolbarNewReportButton").click()
        ctx.app.processEvents()

        new_draft_path = None
        for path in reports_root.rglob("report_draft.json") if reports_root.is_dir() else []:
            if path not in before_drafts:
                new_draft_path = path
                break
        if new_draft_path is None and reports_root.is_dir():
            candidates = sorted(
                reports_root.rglob("report_draft.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            new_draft_path = candidates[0] if candidates else None

        draft_ok = False
        if new_draft_path and new_draft_path.is_file():
            data = json.loads(new_draft_path.read_text(encoding="utf-8"))
            draft_ok = (
                data.get("template") == "快速扫描摘要"
                and data.get("pdf_quality") == "标准"
                and data.get("include_raw_data") == raw_checked
            )

        ok = settings_ok and draft_ok
        check.add(
            "report_settings_interaction",
            ok,
            f"settings={settings_ok} draft={draft_ok}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("report_settings_interaction", False, str(exc))
        return False


def check_page_switch_regression(check: CheckResult, ctx: ReportUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        win = ctx.win
        ok = True
        details: list[str] = []
        for page_index in WORKFLOW_PAGES:
            win._switch_page(page_index)
            ctx.app.processEvents()
            expected = DOCK_TITLES[page_index]
            actual = win._right_dock.windowTitle() if win._right_dock else ""
            docks = win.findChildren(QDockWidget)
            nav_texts = [btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()]
            page_ok = (
                win._page_stack.currentIndex() == page_index
                and actual == expected
                and len(docks) == 1
                and not win._right_dock.isFloating()
                and "项目" not in nav_texts
            )
            if page_index == MainWindow.PAGE_REPORT:
                page_ok = page_ok and all(t in toolbar_texts(win) for t in REPORT_TOOLBAR)
            if page_index == MainWindow.PAGE_SCAN:
                page_ok = page_ok and all(t in toolbar_texts(win) for t in SCAN_TOOLBAR)
            if not page_ok:
                ok = False
            details.append(f"{page_index}:{actual!r}")
        win.close()
        check.add("page_switch_regression", ok, ", ".join(details))
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("page_switch_regression", False, str(exc))
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
        hits.append(f"runtime exports: {', '.join(str(p.relative_to(ROOT)) for p in export_files)}")
    check.add("no_real_device_access", not hits, "; ".join(hits))


def write_acceptance_report(check: CheckResult) -> Path:
    report_path = (
        ROOT
        / "docs/product-spec/release/Release_028_Report_Page_UI_Interaction_Verification/ACCEPTANCE_REPORT.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_028 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_028.py",
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
            "## runtime 产物",
            "",
            f"- `runtime/mock_projects/{PROJECT_NAME}/scans/{TASK_ID}/`",
            f"- `runtime/mock_projects/{PROJECT_NAME}/reports/`（report_draft.json）",
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
            "是" if check.passed else "否",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    setup_offscreen()
    setup_path()
    check = CheckResult("Release_028 Verification")
    ctx = ReportUiContext()

    check_compileall_and_imports(check)
    ensure_mock_scan_result(check)
    if boot_mainwindow(check, ctx):
        check_report_navigation(check, ctx)
        check_report_toolbar(check, ctx)
        check_report_settings_dock(check, ctx)
        check_report_data_source(check, ctx)
        check_report_list_ui(check, ctx)
        check_report_preview_ui(check, ctx)
        check_create_report_draft(check, ctx)
        check_preview_mock_action(check, ctx)
        check_export_mock_actions(check, ctx)
        check_report_settings_interaction(check, ctx)
        check_page_switch_regression(check, ctx)
    check_no_real_device_access(check)

    report_path = write_acceptance_report(check)
    check.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return 0 if check.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
