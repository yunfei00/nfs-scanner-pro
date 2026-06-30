#!/usr/bin/env python3
"""Release_027 自动验收 — Analysis Page UI Interaction Verification。"""

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

TASK_ID = "ST-VERIFY-027"
ANALYSIS_IMPORTS = (
    "nfs_scanner_pro.ui.main_window",
    "nfs_scanner_pro.ui.pages.analysis_page",
    "nfs_scanner_pro.ui.analysis_parameter_dock",
    "nfs_scanner_pro.analysis.analysis_data_source_mock",
    "nfs_scanner_pro.analysis.analysis_dataset_mock",
    "nfs_scanner_pro.scan.scan_result_persistence_mock",
)

WORKFLOW_PAGES = (0, 1, 2, 3, 2)


def _status_text(win) -> str:
    return win._status._message.text()


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
        for mod in ANALYSIS_IMPORTS:
            try:
                __import__(mod)
            except Exception as exc:  # noqa: BLE001
                failed.append(f"{mod}: {exc}")
                ok = False
    check.add("compileall", ok, "; ".join(failed) if failed else "")


class AnalysisUiContext:
    def __init__(self) -> None:
        self.app = None
        self.win = None


def boot_mainwindow(check: CheckResult, ctx: AnalysisUiContext) -> bool:
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


def check_analysis_navigation(check: CheckResult, ctx: AnalysisUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QLabel

        from nfs_scanner_pro.ui.main_window import MainWindow

        win = ctx.win
        nav_btn = win._nav._buttons[MainWindow.PAGE_ANALYSIS]
        nav_btn.click()
        ctx.app.processEvents()

        crumb = win._analysis_page.findChild(QLabel, "breadcrumbBar")
        crumb_text = crumb.text() if crumb else ""
        status = _status_text(win)
        dock_title = win._right_dock.windowTitle() if win._right_dock else ""
        nav_checked = nav_btn.isChecked()

        ok = (
            win._current_page == MainWindow.PAGE_ANALYSIS
            and win._page_stack.currentIndex() == MainWindow.PAGE_ANALYSIS
            and nav_checked
            and dock_title == "分析参数"
            and ("分析就绪" in status or "Mock 扫描结果" in status or "已加载" in status)
            and PROJECT_NAME in crumb_text
            and "CPU_Area" in crumb_text
            and "ScanTask" in crumb_text
            and "Trace" in crumb_text
            and "GHz" in crumb_text
        )
        check.add(
            "analysis_navigation",
            ok,
            f"dock={dock_title!r} status={status!r}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("analysis_navigation", False, str(exc))
        return False


def check_analysis_dock_content(check: CheckResult, ctx: AnalysisUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QGroupBox, QPushButton

        win = ctx.win
        panel = win._analysis_panel
        groups = {g.title(): g for g in panel.findChildren(QGroupBox)}
        required_groups = ("数据源", "显示设置", "光标", "导出")
        group_ok = all(name in groups for name in required_groups)

        control = panel.control_panel
        widgets_ok = all(
            w is not None
            for w in (
                panel.data_source_panel._task_combo,
                control._trace_combo,
                control._freq_combo,
                control._mode_combo,
                control._lut_selector,
                control._vmin_edit,
                control._vmax_edit,
                control._opacity_slider,
            )
        )
        export_btns = {
            btn.text(): btn
            for btn in panel.findChildren(QPushButton)
            if btn.objectName().startswith(("export", "save"))
        }
        export_ok = all(
            text in export_btns
            for text in ("导出热力图图片", "导出当前读数", "保存分析快照")
        )
        ok = group_ok and widgets_ok and export_ok
        check.add(
            "analysis_dock_content",
            ok,
            f"groups={list(groups.keys())}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("analysis_dock_content", False, str(exc))
        return False


def check_analysis_data_source(check: CheckResult, ctx: AnalysisUiContext) -> bool:
    try:
        from nfs_scanner_pro.analysis.analysis_data_source_mock import AnalysisDataSourceMock

        win = ctx.win
        ds = AnalysisDataSourceMock()
        projects = ds.list_projects()
        tasks = ds.list_scan_tasks(PROJECT_NAME)
        dataset = ds.build_dataset(PROJECT_NAME, TASK_ID)
        readout = dataset.cursor_readout()
        empty = ds.build_dataset("MissingProject_XYZ", "ST-MISSING")
        amp_key = "amplitude" if "amplitude" in readout else "amp"

        combo = win._analysis_panel.data_source_panel._task_combo
        combo_ok = TASK_ID in [combo.itemText(i) for i in range(combo.count())]
        switch_status = ""
        if len(tasks) > 1:
            other = next(t for t in tasks if t != TASK_ID)
            win._analysis_page._on_scan_task_selected(other)
            ctx.app.processEvents()
            switch_status = _status_text(win)
        win._analysis_page._on_scan_task_selected(TASK_ID)
        ctx.app.processEvents()
        status = _status_text(win)

        ok = (
            PROJECT_NAME in projects
            and TASK_ID in tasks
            and not dataset.is_empty()
            and all(k in readout for k in ("x", "y", "z", "frequency", amp_key, "phase"))
            and empty.is_empty()
            and combo_ok
            and (
                "已加载分析数据源" in switch_status
                or "已加载分析数据源" in status
                or "分析就绪" in status
            )
        )
        check.add(
            "analysis_data_source",
            ok,
            f"tasks={len(tasks)} status={status!r}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("analysis_data_source", False, str(exc))
        return False


def check_trace_frequency_lut_controls(check: CheckResult, ctx: AnalysisUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QLabel

        win = ctx.win
        control = win._analysis_panel.control_panel
        crumb = win._analysis_page.findChild(QLabel, "breadcrumbBar")
        statuses: list[str] = []

        def snap() -> None:
            ctx.app.processEvents()
            statuses.append(_status_text(win))

        trace_before = control._trace_combo.currentText()
        trace_target = "Trace 2" if trace_before == "Trace 1" else "Trace 1"
        control._trace_combo.setCurrentText(trace_target)
        snap()

        freqs = [control._freq_combo.itemText(i) for i in range(control._freq_combo.count())]
        freq_target = freqs[1] if len(freqs) > 1 else freqs[0]
        control._freq_combo.setCurrentText(freq_target)
        snap()

        mode_target = "相位" if control._mode_combo.currentText() == "幅度" else "幅度"
        control._mode_combo.setCurrentText(mode_target)
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
        check.add(
            "trace_frequency_lut_controls",
            ok,
            f"trace={trace_target} freq={freq_target} updates={len(statuses)}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("trace_frequency_lut_controls", False, str(exc))
        return False


def check_cursor_readout(check: CheckResult, ctx: AnalysisUiContext) -> bool:
    try:
        win = ctx.win
        panel = win._analysis_panel.control_panel._cursor_panel
        labels = panel._labels
        values_ok = all(labels[k].text() not in ("", "—") for k in ("x", "y", "z", "frequency", "amp", "phase"))

        panel._lock_btn.click()
        ctx.app.processEvents()
        lock_status = _status_text(win)

        panel._lock_btn.click()
        ctx.app.processEvents()

        copy_btn = panel.findChild(type(panel._lock_btn), "cursorCopyButton")
        copy_btn.click()
        ctx.app.processEvents()
        copy_status = _status_text(win)

        ok = (
            values_ok
            and ("光标已锁定" in lock_status or "锁定" in lock_status)
            and ("读数已复制" in copy_status or "复制" in copy_status)
        )
        check.add(
            "cursor_readout",
            ok,
            f"x={labels['x'].text()} lock={lock_status!r}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("cursor_readout", False, str(exc))
        return False


def check_export_mock_actions(check: CheckResult, ctx: AnalysisUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QPushButton

        win = ctx.win
        export_actions = (
            ("exportHeatmapButton", "热力图"),
            ("exportReadoutButton", "读数"),
            ("saveSnapshotButton", "快照"),
        )
        runtime_dir = ROOT / "runtime"
        before = {
            p.resolve()
            for p in runtime_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in {".png", ".pdf", ".xlsx", ".csv"}
        }
        statuses: list[str] = []
        for obj_name, _ in export_actions:
            btn = win._analysis_panel.findChild(QPushButton, obj_name)
            btn.click()
            for _ in range(20):
                ctx.app.processEvents()
                time.sleep(0.03)
            statuses.append(_status_text(win))

        after = {
            p.resolve()
            for p in runtime_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in {".png", ".pdf", ".xlsx", ".csv"}
        }
        new_files = after - before
        ok = all("Mock" in s for s in statuses) and not new_files
        check.add(
            "export_mock_actions",
            ok,
            "; ".join(statuses),
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("export_mock_actions", False, str(exc))
        return False


def check_analysis_canvas_state(check: CheckResult, ctx: AnalysisUiContext) -> bool:
    try:
        from nfs_scanner_pro.analysis.analysis_data_source_mock import AnalysisDataSourceMock

        page = ctx.win._analysis_page
        ds = AnalysisDataSourceMock()
        empty = ds.build_dataset("MissingProject_XYZ", "ST-NONE")

        has_view = page._view is not None
        has_color_scale = hasattr(page, "_color_scale") and page._color_scale is not None
        has_position = page._position_overlay is not None
        heatmap_visible = page._view._heat_item.opacity() > 0
        empty_hidden = not page._empty_overlay.isVisible()
        empty_ok = empty.is_empty()

        ok = (
            has_view
            and has_color_scale
            and has_position
            and heatmap_visible
            and empty_hidden
            and empty_ok
        )
        check.add(
            "analysis_canvas_state",
            ok,
            f"heatmap_opacity={page._view._heat_item.opacity():.2f} empty_ok={empty_ok}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("analysis_canvas_state", False, str(exc))
        return False


def check_page_switch_regression(check: CheckResult, ctx: AnalysisUiContext) -> bool:
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
    check.add("no_real_device_access", not hits, "; ".join(hits))


def write_acceptance_report(check: CheckResult) -> Path:
    report_path = (
        ROOT
        / "docs/product-spec/release/Release_027_Analysis_Page_UI_Interaction_Verification/ACCEPTANCE_REPORT.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_027 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_027.py",
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
            "是" if check.passed else "否",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    setup_offscreen()
    setup_path()
    check = CheckResult("Release_027 Verification")
    ctx = AnalysisUiContext()

    check_compileall_and_imports(check)
    ensure_mock_scan_result(check)
    if boot_mainwindow(check, ctx):
        check_analysis_navigation(check, ctx)
        check_analysis_dock_content(check, ctx)
        check_analysis_data_source(check, ctx)
        check_trace_frequency_lut_controls(check, ctx)
        check_cursor_readout(check, ctx)
        check_export_mock_actions(check, ctx)
        check_analysis_canvas_state(check, ctx)
        check_page_switch_regression(check, ctx)
    check_no_real_device_access(check)

    report_path = write_acceptance_report(check)
    check.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return 0 if check.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
