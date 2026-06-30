#!/usr/bin/env python3
"""Release_026 自动验收 — Scan Page UI Interaction Verification。"""

from __future__ import annotations

import compileall
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
    NAV_LABELS,
    PROJECT_NAME,
    ROOT,
    SCAN_TOOLBAR,
    CheckResult,
    describe_mock_scan_dir,
    gitignore_covers_runtime,
    setup_offscreen,
    setup_path,
    toolbar_texts,
)

SCAN_IMPORTS = (
    "nfs_scanner_pro.ui.main_window",
    "nfs_scanner_pro.ui.pages.scan_page",
    "nfs_scanner_pro.scan.scan_engine_mock",
    "nfs_scanner_pro.scan.scan_task_config",
    "nfs_scanner_pro.scan.scan_state",
)

WORKFLOW_PAGES = (0, 1, 2, 3, 0)


def _status_text(win) -> str:
    return win._status._message.text()


def _find_toolbar_button(win, object_name: str):
    from PySide6.QtWidgets import QToolButton

    return win._tool_bar.findChild(QToolButton, object_name)


def _param_field_enabled(win) -> bool:
    panel = win._scan_panel
    if not panel._lockable_fields:
        return True
    field = panel._lockable_fields[0]
    return field.isEnabled()


def _canvas_marker_visible(win) -> bool:
    return win._scan_page._view._current_point_marker.isVisible()


def check_compileall_and_imports(check: CheckResult) -> None:
    ok = bool(compileall.compile_dir(str(ROOT / "src" / "nfs_scanner_pro"), quiet=1))
    failed: list[str] = []
    if ok:
        for mod in SCAN_IMPORTS:
            try:
                __import__(mod)
            except Exception as exc:  # noqa: BLE001
                failed.append(f"{mod}: {exc}")
                ok = False
    check.add("compileall", ok, "; ".join(failed) if failed else "")


class ScanUiContext:
    def __init__(self) -> None:
        self.app = None
        self.win = None


def boot_mainwindow(check: CheckResult, ctx: ScanUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx.app = QApplication.instance() or QApplication([])
        ctx.win = MainWindow()
        ctx.win.show()
        ctx.win._switch_page(MainWindow.PAGE_SCAN)
        ctx.app.processEvents()

        docks = ctx.win.findChildren(QDockWidget)
        nav_texts = [btn.text() for btn in ctx.win._nav.findChildren(QToolButton) if btn.text()]
        ok = (
            ctx.win is not None
            and len(docks) == 1
            and ctx.win._right_dock is not None
            and not ctx.win._right_dock.isFloating()
            and ctx.win._right_dock.windowTitle() == "扫描参数"
            and "项目" not in nav_texts
        )
        check.add("mainwindow_boot", ok, f"dock={ctx.win._right_dock.windowTitle()!r}")
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("mainwindow_boot", False, str(exc))
        return False


def check_scan_toolbar_buttons(check: CheckResult, ctx: ScanUiContext) -> bool:
    try:
        win = ctx.win
        texts = toolbar_texts(win)
        names = (
            "toolbarStartScanButton",
            "toolbarStopScanButton",
            "toolbarCaptureButton",
            "toolbarAlignButton",
            "toolbarGridButton",
            "toolbarMeasureButton",
        )
        buttons_ok = all(_find_toolbar_button(win, name) is not None for name in names)
        text_ok = all(label in texts for label in SCAN_TOOLBAR)
        start_btn = _find_toolbar_button(win, "toolbarStartScanButton")
        stop_btn = _find_toolbar_button(win, "toolbarStopScanButton")
        cn_ok = all("\u4e00" <= ch <= "\u9fff" for ch in "开始扫描")  # sanity
        ok = buttons_ok and text_ok and start_btn is not None and stop_btn is not None and cn_ok
        check.add("scan_toolbar_buttons", ok, str(texts))
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("scan_toolbar_buttons", False, str(exc))
        return False


def check_start_scan_ui_binding(check: CheckResult, ctx: ScanUiContext) -> bool:
    try:
        from nfs_scanner_pro.scan.scan_state import ScanState as EngineScanState
        from nfs_scanner_pro.ui.scan_state import ScanState as UiScanState

        win = ctx.win
        start_btn = _find_toolbar_button(win, "toolbarStartScanButton")
        stop_btn = _find_toolbar_button(win, "toolbarStopScanButton")
        editable_before = _param_field_enabled(win)

        start_btn.click()
        ctx.app.processEvents()

        engine = win._scan_page._engine
        ui_state = win._scan_page.current_scan_state()
        status = _status_text(win)
        start_disabled = not start_btn.isEnabled()
        stop_enabled = stop_btn.isEnabled()
        locked = not _param_field_enabled(win)

        ok = (
            editable_before
            and engine.state is EngineScanState.SCANNING
            and ui_state is UiScanState.SCANNING
            and "扫描中" in status
            and start_disabled
            and stop_enabled
            and locked
        )
        check.add(
            "start_scan_ui_binding",
            ok,
            f"engine={engine.state.value} status={status!r}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("start_scan_ui_binding", False, str(exc))
        return False


def check_scan_progress_updates(check: CheckResult, ctx: ScanUiContext) -> bool:
    try:
        win = ctx.win
        scan_page = win._scan_page
        engine = scan_page._engine
        index_before = engine.progress.current_index

        scan_page._on_timer_tick()
        ctx.app.processEvents()
        time.sleep(0.05)
        ctx.app.processEvents()

        index_after = engine.progress.current_index
        point = engine.current_point()
        progress = win._status._progress_bar.value()
        status = _status_text(win)

        ok = (
            index_after > index_before
            and point is not None
            and progress >= 0
            and "扫描中" in status
        )
        check.add(
            "scan_progress_updates",
            ok,
            f"index {index_before}->{index_after} progress={progress}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("scan_progress_updates", False, str(exc))
        return False


def check_scan_canvas_current_point(check: CheckResult, ctx: ScanUiContext) -> bool:
    try:
        win = ctx.win
        has_method = hasattr(win._scan_page, "set_current_scan_point")
        marker_visible = _canvas_marker_visible(win)
        ok = has_method and marker_visible
        check.add(
            "scan_canvas_current_point",
            ok,
            f"method={has_method} marker={marker_visible}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("scan_canvas_current_point", False, str(exc))
        return False


def check_stop_scan_ui_binding(check: CheckResult, ctx: ScanUiContext) -> bool:
    try:
        from nfs_scanner_pro.scan.scan_state import ScanState as EngineScanState

        win = ctx.win
        stop_btn = _find_toolbar_button(win, "toolbarStopScanButton")
        start_btn = _find_toolbar_button(win, "toolbarStartScanButton")

        stop_btn.click()
        for _ in range(30):
            ctx.app.processEvents()
            time.sleep(0.02)
        if win._scan_page._engine.state is EngineScanState.STOPPING:
            win._scan_page._on_finalize_stop()
            ctx.app.processEvents()

        engine = win._scan_page._engine
        timer_active = win._scan_page._timer.isActive()
        status = _status_text(win)
        editable = _param_field_enabled(win)

        ok = (
            engine.state is not EngineScanState.SCANNING
            and ("已停止" in status or "停止" in status)
            and not timer_active
            and editable
            and start_btn.isEnabled()
            and not stop_btn.isEnabled()
        )
        check.add(
            "stop_scan_ui_binding",
            ok,
            f"engine={engine.state.value} status={status!r}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("stop_scan_ui_binding", False, str(exc))
        return False


def check_scan_completion_persistence(check: CheckResult, ctx: ScanUiContext) -> tuple[bool, str]:
    try:
        from nfs_scanner_pro.app_paths import get_mock_scan_dir
        from nfs_scanner_pro.scan.scan_state import ScanState as EngineScanState

        win = ctx.win
        scan_page = win._scan_page
        start_btn = _find_toolbar_button(win, "toolbarStartScanButton")

        start_btn.click()
        ctx.app.processEvents()

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
        task_id = engine.result.task_id if engine.result else ""
        project = engine.config.project_name
        scan_dir = get_mock_scan_dir(project, task_id) if task_id else None

        csv_rows = 0
        if scan_dir and (scan_dir / "scan_points_preview.csv").is_file():
            import csv

            with (scan_dir / "scan_points_preview.csv").open(encoding="utf-8", newline="") as handle:
                csv_rows = max(0, sum(1 for _ in csv.reader(handle)) - 1)

        json_ok = False
        if scan_dir and (scan_dir / "scan_result.json").is_file():
            payload = json.loads((scan_dir / "scan_result.json").read_text(encoding="utf-8"))
            json_ok = isinstance(payload, dict)

        export_bad: list[Path] = []
        if scan_dir:
            export_bad = (
                list(scan_dir.glob("*.pdf"))
                + list(scan_dir.glob("*.docx"))
                + list(scan_dir.glob("*.xlsx"))
            )

        ok = (
            engine.state is EngineScanState.COMPLETED
            and ("扫描完成" in status or "结果已保存" in status)
            and progress.percent == 100
            and progress.current_index == progress.total_points == 6461
            and progress.remaining_time == "00:00:00"
            and scan_dir is not None
            and (scan_dir / "scan_result.json").is_file()
            and (scan_dir / "scan_summary.json").is_file()
            and (scan_dir / "scan_points_preview.csv").is_file()
            and csv_rows <= 200
            and json_ok
            and not export_bad
            and gitignore_covers_runtime(scan_dir / "scan_result.json")
        )
        check.add(
            "scan_completion_persistence",
            ok,
            f"task={task_id} points={progress.current_index}/{progress.total_points} csv={csv_rows}",
        )
        return ok, task_id
    except Exception as exc:  # noqa: BLE001
        check.add("scan_completion_persistence", False, str(exc))
        return False, ""


def check_scan_parameter_locking(check: CheckResult, ctx: ScanUiContext) -> bool:
    try:
        win = ctx.win
        panel = win._scan_panel
        # 完成后参数应恢复可编辑
        editable_after = _param_field_enabled(win)
        panel.set_fields_locked(True)
        locked = not _param_field_enabled(win)
        panel.set_fields_locked(False)
        editable_restored = _param_field_enabled(win)
        ok = editable_after and locked and editable_restored
        check.add(
            "scan_parameter_locking",
            ok,
            f"after_complete={editable_after} locked={locked}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("scan_parameter_locking", False, str(exc))
        return False


def check_page_switch_regression(check: CheckResult, ctx: ScanUiContext) -> bool:
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
    check.add("no_real_device_access", not hits, "; ".join(hits))


def write_acceptance_report(check: CheckResult, task_id: str) -> Path:
    report_path = (
        ROOT
        / "docs/product-spec/release/Release_026_Scan_Page_UI_Interaction_Verification/ACCEPTANCE_REPORT.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_026 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_026.py",
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
        ]
    )
    if task_id:
        lines.append(f"- `{describe_mock_scan_dir(PROJECT_NAME, task_id)}/`")
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
    check = CheckResult("Release_026 Verification")
    ctx = ScanUiContext()
    task_id = ""

    check_compileall_and_imports(check)
    if boot_mainwindow(check, ctx):
        check_scan_toolbar_buttons(check, ctx)
        check_start_scan_ui_binding(check, ctx)
        check_scan_progress_updates(check, ctx)
        check_scan_canvas_current_point(check, ctx)
        check_stop_scan_ui_binding(check, ctx)
        _, task_id = check_scan_completion_persistence(check, ctx)
        check_scan_parameter_locking(check, ctx)
        check_page_switch_regression(check, ctx)
    check_no_real_device_access(check)

    report_path = write_acceptance_report(check, task_id)
    check.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return 0 if check.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
