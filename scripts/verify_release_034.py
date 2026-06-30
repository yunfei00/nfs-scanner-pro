#!/usr/bin/env python3
"""Release_034 自动验收 — Project Workspace UI Verification。"""

from __future__ import annotations

import compileall
import json
import os
import subprocess
import sys
import time
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
    "nfs_scanner_pro.ui.widgets.top_menu_bar",
    "nfs_scanner_pro.ui.dialogs.project_dialogs",
    "nfs_scanner_pro.project_mock",
    "nfs_scanner_pro.workspace_state_mock",
    "nfs_scanner_pro.app_paths",
)

FILE_MENU_ACTIONS = (
    "新建项目",
    "打开项目",
    "打开最近项目",
    "保存项目",
    "关闭项目",
    "打开项目文件夹",
    "退出",
)

TOP_MENUS = ("文件(F)", "编辑(E)", "视图(V)", "工具(T)", "设置(S)", "帮助(H)")

RECENT_PROJECTS = ("Demo_Project_001", "iPhone16_Mainboard", "RF_Module_Test")

FORBIDDEN_SCAN_PATHS = MOCK_DEVICE_DIRS + (
    ROOT / "src/nfs_scanner_pro/ui/dialogs",
    ROOT / "src/nfs_scanner_pro/project_mock.py",
    ROOT / "src/nfs_scanner_pro/workspace_state_mock.py",
)

EXPORT_EXTENSIONS = {".pdf", ".docx", ".xlsx"}


class UiContext:
    def __init__(self) -> None:
        self.app = None
        self.win = None

    def require_win(self):
        if self.win is None:
            raise RuntimeError("MainWindow not initialized")


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


def _menu_bar(win):
    top = getattr(win, "_top_menu_bar", None)
    if top is not None and hasattr(top, "_menu_bar"):
        return top._menu_bar
    from PySide6.QtWidgets import QMenuBar

    return win.findChild(QMenuBar)


def _file_menu(win):
    menu_bar = _menu_bar(win)
    if menu_bar is None:
        return None
    for action in menu_bar.actions():
        if action.text().startswith("文件"):
            return action.menu()
    return None


def _file_menu_details(win) -> tuple[list[str], list[str]]:
    menu_bar = _menu_bar(win)
    if menu_bar is None:
        return [], []
    texts: list[str] = []
    recent: list[str] = []
    for top_action in menu_bar.actions():
        if not top_action.text().startswith("文件"):
            continue
        file_menu = top_action.menu()
        if file_menu is None:
            break
        for act in file_menu.actions():
            if act.isSeparator():
                continue
            texts.append(act.text())
            if act.text() == "打开最近项目":
                sub = act.menu()
                if sub is not None:
                    recent = [sub_act.text() for sub_act in sub.actions()]
        break
    return texts, recent


def _trigger_file_action(win, label: str) -> bool:
    menu = _file_menu(win)
    if menu is None:
        return False
    for act in menu.actions():
        if act.text() == label:
            act.trigger()
            return True
    return False


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


def _reset_isolated_runtime() -> Path:
    verification_runtime.clean_release_runtime("034")
    runtime_dir = verification_runtime.enter_release_runtime("R034")
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
        runtime_dir = _reset_isolated_runtime()
        setup_path()
        from nfs_scanner_pro.app_paths import get_runtime_dir, get_workspace_state_path

        active = get_runtime_dir().resolve()
        ws_path = get_workspace_state_path()
        ws_path.parent.mkdir(parents=True, exist_ok=True)
        ws_path.write_text("{}", encoding="utf-8")

        ok = (
            active == runtime_dir.resolve()
            and "verification/R034" in active.as_posix()
            and ws_path.is_file()
            and "verification/R034" in ws_path.as_posix()
        )
        git_ok, git_detail = verification_runtime.assert_runtime_ignored_by_git()
        after = _list_shared_mock_files()
        ok = ok and git_ok and not (after - baseline)
        detail = f"{ws_path.relative_to(ROOT).as_posix()}; {git_detail}"
        if ok:
            report.pass_check("runtime_isolation", detail)
        else:
            report.fail_check("runtime_isolation", detail)
    except Exception as exc:  # noqa: BLE001
        report.fail_check("runtime_isolation", str(exc))


def check_mainwindow_boot(report: verification_report.VerificationReport) -> None:
    report.start_check("mainwindow_boot")
    _reset_isolated_runtime()
    ctx = UiContext()
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QMenuBar, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx.app = QApplication.instance() or QApplication([])
        ctx.win = MainWindow()
        ctx.win.show()
        _process(ctx.app)

        menu_bar = _menu_bar(ctx.win)
        menu_texts = [a.text() for a in menu_bar.actions()] if menu_bar else []
        nav_texts = [
            btn.text() for btn in ctx.win._nav.findChildren(QToolButton) if btn.text()
        ]
        docks = ctx.win.findChildren(QDockWidget)

        ok = (
            ctx.win is not None
            and len(docks) == 1
            and ctx.win._right_dock is not None
            and not ctx.win._right_dock.isFloating()
            and "项目" not in nav_texts
            and all(label in nav_texts for label in NAV_LABELS)
            and all(label in menu_texts for label in TOP_MENUS)
        )
        if ok:
            report.pass_check("mainwindow_boot", f"menus={len(menu_texts)}")
        else:
            report.fail_check(
                "mainwindow_boot",
                f"nav={nav_texts} menus={menu_texts} docks={len(docks)}",
            )
        ctx.win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("mainwindow_boot", str(exc))


def check_file_menu_project_actions(report: verification_report.VerificationReport) -> None:
    report.start_check("file_menu_project_actions")
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        from nfs_scanner_pro import project_mock

        texts, recent_texts = _file_menu_details(win)
        if not recent_texts:
            recent_texts = project_mock.get_recent_project_names()
        missing = [label for label in FILE_MENU_ACTIONS if label not in texts]
        nav_texts = [
            btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()
        ]
        handlers_ok = all(
            callable(getattr(win, attr, None))
            for attr in (
                "_on_new_project",
                "_on_open_project",
                "_on_save_project",
                "_on_close_project",
                "_on_open_project_folder",
            )
        )

        ok = (
            not missing
            and handlers_ok
            and all(name in recent_texts for name in RECENT_PROJECTS)
            and "项目" not in nav_texts
        )
        if ok:
            report.pass_check("file_menu_project_actions")
        else:
            report.fail_check(
                "file_menu_project_actions",
                f"missing={missing} recent={recent_texts}",
            )
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("file_menu_project_actions", str(exc))


def check_create_project_dialog(report: verification_report.VerificationReport) -> None:
    report.start_check("create_project_dialog")
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication, QPushButton

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.app_paths import get_workspace_state_path
        from nfs_scanner_pro.ui.dialogs.project_dialogs import NewProjectDialog
        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        dlg = NewProjectDialog(win)
        from PySide6.QtWidgets import QWidget

        content = dlg.findChild(QWidget, "projectDialogContent")
        ok = (
            dlg.objectName() == "projectDialog"
            and content is not None
            and dlg._name.text() == "Demo_Project_001"
            and dlg._path.text() == "D:/NFS_Projects/Demo_Project_001"
            and dlg._pcb.text() == "iPhone16_Mainboard"
            and dlg._region.text() == "CPU_Area"
        )
        create_btn = dlg.findChild(QPushButton, "projectDialogPrimaryButton")
        ok = ok and create_btn is not None and create_btn.text() == "创建"

        if ok:
            dlg._pcb.setText("Demo_Project_001")
            create_btn.click()
            name, path, pcb, region = dlg.values()
            project_mock.create_project_mock(name, path, pcb, region)
            win._refresh_project_ui()
            win._set_project_status(f"Mock：项目 {name} 已创建")
            win._capture_and_save_workspace()
            _process(app)
            status = _status_text(win)
            display = project_mock.project_display_name()
            ok = (
                project_mock.get_current_project()["name"] == "Demo_Project_001"
                and display in _breadcrumb_scan(win)
                and "Mock" in status
                and "已创建" in status
                and get_workspace_state_path().is_file()
            )

        if ok:
            report.pass_check("create_project_dialog")
        else:
            report.fail_check("create_project_dialog", _status_text(win))
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("create_project_dialog", str(exc))


def check_open_project_dialog(report: verification_report.VerificationReport) -> None:
    report.start_check("open_project_dialog")
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.app_paths import get_workspace_state_path
        from nfs_scanner_pro.ui.dialogs.project_dialogs import OpenProjectDialog
        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        dlg = OpenProjectDialog(win)
        listed = [
            project_mock.get_recent_projects()[i]["name"]
            for i in range(dlg._list.count())
        ]
        ok = all(name in listed for name in RECENT_PROJECTS)

        target_row = next(
            (
                i
                for i, p in enumerate(project_mock.get_recent_projects())
                if p["name"] == "iPhone16_Mainboard"
            ),
            -1,
        )
        if ok and target_row >= 0:
            dlg._list.setCurrentRow(target_row)
            dlg._accept_selection()
            name = dlg.selected_project_name()
            project_mock.open_project_mock(name)
            win._refresh_project_ui()
            win._set_project_status(f"Mock：已打开项目 {name}")
            win._capture_and_save_workspace()
            _process(app)
            status = _status_text(win)
            display = project_mock.project_display_name()
            ok = (
                project_mock.get_current_project()["name"] == "iPhone16_Mainboard"
                and display in _breadcrumb_scan(win)
                and "Mock" in status
                and "已打开项目" in status
                and get_workspace_state_path().is_file()
            )

        if ok:
            report.pass_check("open_project_dialog")
        else:
            report.fail_check("open_project_dialog", f"listed={listed}")
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("open_project_dialog", str(exc))


def check_recent_project_menu(report: verification_report.VerificationReport) -> None:
    report.start_check("recent_project_menu")
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.app_paths import get_workspace_state_path
        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        recent_texts = [act.text() for act in win._recent_project_menu.actions()]
        ok = all(name in recent_texts for name in RECENT_PROJECTS)

        if ok:
            for action in win._recent_project_menu.actions():
                if action.text() == "RF_Module_Test":
                    action.trigger()
                    break
            _process(app)
            status = _status_text(win)
            display = project_mock.project_display_name()
            ok = (
                project_mock.get_current_project()["name"] == "RF_Module_Test"
                and display in _breadcrumb_scan(win)
                and "Mock" in status
                and "已打开项目" in status
                and get_workspace_state_path().is_file()
            )

        if ok:
            report.pass_check("recent_project_menu")
        else:
            report.fail_check("recent_project_menu", f"recent={recent_texts}")
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("recent_project_menu", str(exc))


def check_save_close_open_folder_mock(report: verification_report.VerificationReport) -> None:
    report.start_check("save_close_open_folder_mock")
    _reset_isolated_runtime()
    before_exports = _runtime_export_files()
    try:
        from PySide6.QtWidgets import QApplication, QToolButton

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.app_paths import get_workspace_state_path
        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        project_mock.open_project_mock("iPhone16_Mainboard")
        win._refresh_project_ui()

        win._on_save_project()
        _process(app)
        save_status = _status_text(win)
        save_ok = "Mock" in save_status and "已保存" in save_status

        win._on_close_project()
        _process(app)
        close_status = _status_text(win)
        nav_texts = [
            btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()
        ]
        close_ok = (
            project_mock.get_current_project().get("status") == "closed"
            and "Mock" in close_status
            and "已关闭" in close_status
            and "项目" not in nav_texts
        )

        project_mock.open_project_mock("Demo_Project_001")
        win._refresh_project_ui()
        win._on_open_project_folder()
        _process(app)
        folder_status = _status_text(win)
        folder_ok = "Mock" in folder_status and "打开项目文件夹" in folder_status

        after_exports = _runtime_export_files()
        ok = (
            save_ok
            and close_ok
            and folder_ok
            and get_workspace_state_path().is_file()
            and not (after_exports - before_exports)
        )
        if ok:
            report.pass_check("save_close_open_folder_mock")
        else:
            report.fail_check(
                "save_close_open_folder_mock",
                f"save={save_ok} close={close_ok} folder={folder_ok}",
            )
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("save_close_open_folder_mock", str(exc))


def check_breadcrumb_sync(report: verification_report.VerificationReport) -> None:
    report.start_check("breadcrumb_sync")
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication, QLabel

        from nfs_scanner_pro import project_mock
        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        project_mock.open_project_mock("iPhone16_Mainboard")
        win._refresh_project_ui()
        display = project_mock.project_display_name()
        scan_ok = display in _breadcrumb_scan(win)

        project_mock.create_project_mock(
            "Demo_Project_001",
            "D:/NFS_Projects/Demo_Project_001",
            "Demo_Project_001",
            "CPU_Area",
        )
        win._refresh_project_ui()
        display = project_mock.project_display_name()
        create_ok = display in _breadcrumb_scan(win)

        project_mock.close_project_mock()
        win._refresh_project_ui()
        closed_ok = "未打开项目" in _breadcrumb_scan(win)

        win._switch_page(win.PAGE_ANALYSIS)
        _process(app)
        analysis_crumb = win._analysis_page.findChild(QLabel, "breadcrumbBar")
        analysis_ok = analysis_crumb is not None and analysis_crumb.text()

        win._switch_page(win.PAGE_REPORT)
        _process(app)
        report_crumb = win._report_page.findChild(QLabel, "breadcrumbBar")
        report_ok = report_crumb is not None and report_crumb.text()

        combined = f"{scan_ok} {create_ok} {closed_ok} {analysis_ok} {report_ok}"
        english_bad = "workspace" in _breadcrumb_scan(win).lower()

        ok = scan_ok and create_ok and closed_ok and analysis_ok and report_ok and not english_bad
        if ok:
            report.pass_check("breadcrumb_sync")
        else:
            report.fail_check("breadcrumb_sync", combined)
        win.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("breadcrumb_sync", str(exc))


def check_workspace_state_persistence(report: verification_report.VerificationReport) -> None:
    report.start_check("workspace_state_persistence")
    _reset_isolated_runtime()
    try:
        setup_path()
        from nfs_scanner_pro import project_mock, workspace_state_mock
        from nfs_scanner_pro.app_paths import get_workspace_state_path

        project = project_mock.get_current_project()
        workspace_state_mock.update_current_project(project)
        workspace_state_mock.update_last_page("analysis")
        workspace_state_mock.update_navigation_expanded(True)
        workspace_state_mock.update_right_dock_visible(False)
        workspace_state_mock.update_window_state(1440, 900, False)

        ws_path = get_workspace_state_path()
        ok = ws_path.is_file() and "verification/R034" in ws_path.as_posix()

        workspace_state_mock.load_workspace_state()
        state, load_ok = workspace_state_mock.load_workspace_state()
        ok = ok and load_ok
        ok = ok and state["current_project"]["name"] == project["name"]
        ok = ok and state["last_page"] == "analysis"
        ok = ok and state["navigation_expanded"] is True
        ok = ok and state["right_dock_visible"] is False
        ok = ok and state["window"]["width"] == 1440
        ok = ok and state["window"]["height"] == 900
        ok = ok and state["window"]["maximized"] is False
        ok = ok and isinstance(state.get("recent_projects"), list)

        if ok:
            report.pass_check(
                "workspace_state_persistence",
                ws_path.relative_to(ROOT).as_posix(),
            )
        else:
            report.fail_check("workspace_state_persistence", json.dumps(state, ensure_ascii=False)[:200])
    except Exception as exc:  # noqa: BLE001
        report.fail_check("workspace_state_persistence", str(exc))


def check_mainwindow_restore(report: verification_report.VerificationReport) -> None:
    report.start_check("mainwindow_restore")
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro import project_mock, workspace_state_mock
        from nfs_scanner_pro.app_paths import get_workspace_state_path
        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win1 = MainWindow()
        win1.show()
        _process(app)

        project_mock.open_project_mock("iPhone16_Mainboard")
        win1._refresh_project_ui()
        win1._switch_page(MainWindow.PAGE_ANALYSIS)
        win1._capture_and_save_workspace()
        _process(app)

        win1.close()
        win1.deleteLater()
        _process(app, 20)

        win2 = MainWindow()
        win2.show()
        _process(app, 20)

        state, _ = workspace_state_mock.load_workspace_state()
        project = project_mock.get_current_project()
        nav_texts = [
            btn.text() for btn in win2._nav.findChildren(QToolButton) if btn.text()
        ]
        docks = win2.findChildren(QDockWidget)

        ok = (
            project.get("name") == "iPhone16_Mainboard"
            and state.get("last_page") == "analysis"
            and win2._current_page == MainWindow.PAGE_ANALYSIS
            and len(docks) == 1
            and win2._right_dock is not None
            and not win2._right_dock.isFloating()
            and "项目" not in nav_texts
            and get_workspace_state_path().is_file()
        )
        if ok:
            report.pass_check("mainwindow_restore")
        else:
            report.fail_check(
                "mainwindow_restore",
                f"page={win2._current_page} project={project.get('name')} last={state.get('last_page')}",
            )
        win2.close()
    except Exception as exc:  # noqa: BLE001
        report.fail_check("mainwindow_restore", str(exc))


def check_page_switch_regression(report: verification_report.VerificationReport) -> None:
    report.start_check("page_switch_regression")
    _reset_isolated_runtime()
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()
        _process(app)

        sequence = (
            MainWindow.PAGE_SCAN,
            MainWindow.PAGE_DEVICE,
            MainWindow.PAGE_ANALYSIS,
            MainWindow.PAGE_REPORT,
            MainWindow.PAGE_SCAN,
        )
        ok = True
        for page_index in sequence:
            win._switch_page(page_index)
            _process(app)
            docks = win.findChildren(QDockWidget)
            nav_texts = [
                btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()
            ]
            dock_title = win._right_dock.windowTitle() if win._right_dock else ""
            toolbar = toolbar_texts(win)
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

        if ok:
            report.pass_check("page_switch_regression")
        else:
            report.fail_check("page_switch_regression", f"page={page_index} dock={dock_title}")
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
    export_hits = _runtime_export_files()
    if export_hits:
        hits.append(f"runtime exports: {len(export_hits)}")
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
        / "docs/product-spec/release/Release_034_Project_Workspace_UI_Verification/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    setup_path()
    from nfs_scanner_pro.app_paths import get_workspace_state_path

    ws_rel = get_workspace_state_path()
    try:
        ws_display = ws_rel.relative_to(ROOT).as_posix()
    except ValueError:
        ws_display = str(ws_rel)
    lines = [
        "# Release_034 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_034.py",
        "python scripts/verify_all.py --only 034",
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
            "- `runtime/verification/R034/`",
            "",
            "## workspace_state_mock.json 路径",
            "",
            f"- `{ws_display}`",
            "",
            "## 是否接真实设备",
            "",
            "否",
            "",
            "## 是否打开系统资源管理器",
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
    verification_runtime.enter_release_runtime("R034")
    report = verification_report.VerificationReport("034")

    check_compileall(report)
    check_runtime_isolation(report)
    check_mainwindow_boot(report)
    check_file_menu_project_actions(report)
    check_create_project_dialog(report)
    check_open_project_dialog(report)
    check_recent_project_menu(report)
    check_save_close_open_folder_mock(report)
    check_breadcrumb_sync(report)
    check_workspace_state_persistence(report)
    check_mainwindow_restore(report)
    check_page_switch_regression(report)
    check_no_real_device_access(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
