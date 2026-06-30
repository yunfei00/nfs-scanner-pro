"""共享验收工具 — Release_023。

Release_031+：隔离 runtime 数据请优先使用 verification_runtime.py（runtime/verification/Rxxx/）。
"""

from __future__ import annotations

import compileall
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

GITIGNORE_REQUIRED = (
    "__pycache__/",
    "*.pyc",
    "runtime/",
    "runtime/**/*.json",
    "runtime/**/*.csv",
)

FORBIDDEN_PATTERNS = (
    "serial.Serial",
    "pyvisa",
    "cv2.VideoCapture",
    "socket.create_connection",
    "subprocess.Popen",
    "os.startfile",
)

MOCK_DEVICE_DIRS = (
    ROOT / "src/nfs_scanner_pro/devices",
    ROOT / "src/nfs_scanner_pro/scan",
    ROOT / "src/nfs_scanner_pro/analysis",
    ROOT / "src/nfs_scanner_pro/report",
)

DOCK_TITLES = ("扫描参数", "设备配置", "分析参数", "报告设置")
SCAN_TOOLBAR = ("开始扫描", "停止扫描", "拍照", "区域对齐", "网格", "测量")
REPORT_TOOLBAR = ("新建报告", "预览", "导出 PDF", "导出 Word", "导出 Excel")
NAV_LABELS = ("扫描", "设备", "分析", "报告")
PROJECT_NAME = "iPhone16_Mainboard"


def setup_offscreen() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def setup_path() -> None:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))


class CheckResult:
    def __init__(self, title: str) -> None:
        self.title = title
        self.results: list[tuple[str, bool, str]] = []

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.results.append((name, ok, detail))

    @property
    def passed(self) -> bool:
        return all(ok for _, ok, _ in self.results)

    def safe(self, text: str) -> str:
        encoding = sys.stdout.encoding or "utf-8"
        return text.encode(encoding, errors="backslashreplace").decode(
            encoding,
            errors="backslashreplace",
        )

    def print_report(self) -> None:
        print(f"{self.title}\n")
        for name, ok, detail in self.results:
            status = "PASS" if ok else "FAIL"
            line = f"[{status}] {name}"
            if detail:
                line += f" — {detail}"
            print(self.safe(line))
        print()
        if self.passed:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")
            print("\nFailures:")
            for name, ok, detail in self.results:
                if not ok:
                    print(f"  - {name}: {detail or 'failed'}")


def check_compileall(check: CheckResult, name: str = "compileall") -> bool:
    ok = bool(compileall.compile_dir(str(SRC / "nfs_scanner_pro"), quiet=1))
    check.add(name, ok)
    return ok


def check_gitignore(check: CheckResult, name: str = "gitignore") -> bool:
    gitignore_path = ROOT / ".gitignore"
    text = gitignore_path.read_text(encoding="utf-8") if gitignore_path.is_file() else ""
    missing = [rule for rule in GITIGNORE_REQUIRED if rule not in text]
    ok = not missing
    check.add(name, ok, ", ".join(missing) if missing else "ok")
    return ok


def check_module_imports(check: CheckResult, modules: tuple[str, ...], name: str) -> bool:
    failed: list[str] = []
    for mod in modules:
        try:
            __import__(mod)
        except Exception as exc:  # noqa: BLE001
            failed.append(f"{mod}: {exc}")
    ok = not failed
    check.add(name, ok, "; ".join(failed))
    return ok


def check_no_real_device_access(
    check: CheckResult,
    *,
    dirs: tuple[Path, ...] = MOCK_DEVICE_DIRS,
    name: str = "no_real_device_access",
) -> bool:
    hits: list[str] = []
    for base in dirs:
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
    ok = not hits
    check.add(name, ok, "; ".join(hits))
    return ok


def toolbar_texts(main_window) -> list[str]:
    from PySide6.QtWidgets import QToolButton

    return [
        btn.text()
        for btn in main_window._tool_bar.findChildren(QToolButton)
        if btn.text()
    ]


def check_mainwindow_offscreen(check: CheckResult) -> None:
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        win.show()

        docks = win.findChildren(QDockWidget)
        dock_ok = len(docks) == 1
        check.add("mainwindow_single_dock", dock_ok, f"count={len(docks)}")

        not_floating = win._right_dock is not None and not win._right_dock.isFloating()
        check.add("right_dock_not_floating", not_floating)

        nav_texts = [btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()]
        nav_ok = "项目" not in nav_texts and all(label in nav_texts for label in NAV_LABELS)
        check.add("no_project_in_left_nav", nav_ok, str(nav_texts))

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
        report_ok = all(label in toolbar_texts(win) for label in REPORT_TOOLBAR)
        check.add("report_toolbar", report_ok, str(toolbar_texts(win)))

        win._switch_page(MainWindow.PAGE_SCAN)
        app.processEvents()
        scan_ok = all(label in toolbar_texts(win) for label in SCAN_TOOLBAR)
        check.add("scan_toolbar_restore", scan_ok, str(toolbar_texts(win)))

        win.close()
    except Exception as exc:  # noqa: BLE001
        check.add("mainwindow_offscreen", False, str(exc))


def gitignore_covers_runtime(path: Path) -> bool:
    """检查路径是否被 .gitignore 规则语义覆盖（文本匹配）。"""
    rel = path.relative_to(ROOT).as_posix()
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if "runtime/" in gitignore and rel.startswith("runtime/"):
        return True
    return False


def runtime_export_files(
    extensions: frozenset[str] | None = None,
) -> set[Path]:
    """在当前 active runtime（含 NFS_SCANNER_RUNTIME_DIR）下查找导出类文件。"""
    from nfs_scanner_pro.app_paths import get_runtime_dir

    exts = extensions or frozenset({".pdf", ".docx", ".xlsx", ".png"})
    runtime = get_runtime_dir()
    if not runtime.is_dir():
        return set()
    return {
        p.resolve()
        for p in runtime.rglob("*")
        if p.is_file() and p.suffix.lower() in exts
    }


def _runtime_rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def describe_mock_scan_dir(project_name: str, task_id: str) -> str:
    """返回当前 active runtime 下 mock 扫描目录的仓库相对路径。"""
    setup_path()
    from nfs_scanner_pro.app_paths import get_mock_scan_dir

    return _runtime_rel(get_mock_scan_dir(project_name, task_id))


def describe_mock_report_draft(project_name: str, report_id: str) -> str:
    """返回当前 active runtime 下 report_draft.json 的仓库相对路径。"""
    setup_path()
    from nfs_scanner_pro.app_paths import get_mock_project_dir

    safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in report_id.strip())
    path = get_mock_project_dir(project_name) / "reports" / (safe_id or "RP-UNKNOWN") / "report_draft.json"
    return _runtime_rel(path)


def describe_mock_reports_dir(project_name: str) -> str:
    """返回当前 active runtime 下 mock 报告目录的仓库相对路径。"""
    setup_path()
    from nfs_scanner_pro.app_paths import get_mock_project_dir

    return _runtime_rel(get_mock_project_dir(project_name) / "reports")


def describe_workspace_state() -> str:
    """返回当前 active runtime 下 workspace_state_mock.json 的仓库相对路径。"""
    setup_path()
    from nfs_scanner_pro.app_paths import get_workspace_state_path

    return _runtime_rel(get_workspace_state_path())
