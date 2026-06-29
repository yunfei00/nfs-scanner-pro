"""主窗口 — Release 011 PySide6 Mock 原型（四页）。"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QStackedWidget,
    QTabBar,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui.analysis_parameter_dock import AnalysisParameterDock
from nfs_scanner_pro.ui.device_config_dock import DeviceConfigDock
from nfs_scanner_pro.ui.device_status_bar import DeviceStatusBar
from nfs_scanner_pro.ui.navigation_bar import LeftNavigationBar
from nfs_scanner_pro.ui.pages.analysis_page import AnalysisPage
from nfs_scanner_pro.ui.pages.device_page import DevicePage
from nfs_scanner_pro.ui.pages.report_page import ReportPage
from nfs_scanner_pro.ui.pages.scan_page import ScanPage
from nfs_scanner_pro.ui.report_settings_dock import ReportSettingsDock
from nfs_scanner_pro.ui.scan_parameter_dock import ScanParameterDock
from nfs_scanner_pro.ui.widgets.status_bar import AppStatusBar
from nfs_scanner_pro.ui.widgets.top_menu_bar import TopMenuBar

_SCAN_TOOLBAR = (
    ("toolbarStartScanButton", "开始扫描", "primary", "开始扫描", "扫描中（原型）"),
    ("toolbarStopScanButton", "停止扫描", "danger", "停止扫描", "准备就绪"),
    ("toolbarCaptureButton", "拍照", "secondary", "拍照", None),
    ("toolbarAlignButton", "区域对齐", "secondary", "区域对齐", None),
    ("toolbarGridButton", "网格", "secondary", "网格", None),
    ("toolbarMeasureButton", "测量", "secondary", "测量", None),
)

_REPORT_TOOLBAR = (
    ("toolbarNewReportButton", "新建报告", "primary", "新建报告", None),
    ("toolbarPreviewButton", "预览", "secondary", "预览", None),
    ("toolbarExportPdfButton", "导出 PDF", "secondary", "导出 PDF", None),
    ("toolbarExportWordButton", "导出 Word", "secondary", "导出 Word", None),
    ("toolbarExportExcelButton", "导出 Excel", "secondary", "导出 Excel", None),
)


class MainWindow(QMainWindow):
    WINDOW_TITLE = "近场扫描系统"
    DEFAULT_WIDTH = 1600
    DEFAULT_HEIGHT = 1000
    FRAMELESS_WINDOW = True

    PAGE_SCAN = 0
    PAGE_DEVICE = 1
    PAGE_ANALYSIS = 2
    PAGE_REPORT = 3

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        self._current_page = self.PAGE_SCAN
        self._hidden_docks: list[QDockWidget] = []
        self._page_docks: list[QDockWidget] = []

        if self.FRAMELESS_WINDOW:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
            )

        menu_bar = QMenuBar(self)
        self._build_menu_bar(menu_bar)
        if self.FRAMELESS_WINDOW:
            self._top_menu_bar = TopMenuBar(self, menu_bar)
            self.setMenuWidget(self._top_menu_bar)
        else:
            self.setMenuBar(menu_bar)
        self._tool_bar = QToolBar("主工具栏", self)
        self._tool_bar.setObjectName("mainToolBar")
        self._tool_bar.setMovable(False)
        self._tool_bar.setFloatable(False)
        self._tool_bar.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)
        self._tool_bar.setIconSize(QSize(18, 18))
        self._tool_bar.setFixedHeight(54)
        self.addToolBar(self._tool_bar)
        self._build_central()
        self._build_docks()
        self._status = AppStatusBar(self)
        self._wire_view_menu()
        self._rebuild_toolbar(self.PAGE_SCAN)
        self._switch_page(self.PAGE_SCAN)

    def _build_menu_bar(self, menu_bar: QMenuBar) -> None:
        menu_bar.setObjectName("menuBar")

        file_menu = menu_bar.addMenu("文件(F)")
        file_actions = [
            ("新建项目", self._mock_file_action),
            ("打开项目", self._mock_file_action),
            ("打开最近项目", self._mock_file_action),
            ("保存项目", self._mock_file_action),
            None,
            ("关闭项目", self._mock_file_action),
            ("打开项目文件夹", self._mock_file_action),
            None,
            ("退出", self.close),
        ]
        for item in file_actions:
            if item is None:
                file_menu.addSeparator()
            else:
                label, slot = item
                act = file_menu.addAction(label)
                act.triggered.connect(slot)

        menu_bar.addMenu("编辑(E)")
        view_menu = menu_bar.addMenu("视图(V)")

        self._action_param_panel = QAction("显示参数面板", self)
        self._action_param_panel.setCheckable(True)
        self._action_param_panel.setChecked(True)
        view_menu.addAction(self._action_param_panel)

        for label in (
            "显示日志面板",
            "显示频谱面板",
            "显示统计面板",
            "显示色带",
            "显示小地图",
        ):
            act = QAction(label, self)
            act.setCheckable(True)
            act.setEnabled(False)
            view_menu.addAction(act)

        view_menu.addSeparator()
        reset_act = QAction("重置布局", self)
        reset_act.triggered.connect(self._mock_log("重置布局"))
        view_menu.addAction(reset_act)

        menu_bar.addMenu("工具(T)")
        menu_bar.addMenu("设置(S)")
        menu_bar.addMenu("帮助(H)")

    def _rebuild_toolbar(self, page_index: int) -> None:
        self._tool_bar.clear()
        spec = _REPORT_TOOLBAR if page_index == self.PAGE_REPORT else _SCAN_TOOLBAR
        for index, (obj_name, text, variant, log_msg, state_msg) in enumerate(spec):
            btn = QToolButton(self)
            btn.setObjectName(obj_name)
            btn.setText(text)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            btn.setProperty("variant", variant)
            btn.setFixedHeight(36)
            btn.clicked.connect(self._toolbar_action(log_msg, state_msg))
            self._tool_bar.addWidget(btn)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            if index == 1:
                self._tool_bar.addSeparator()

    def _build_central(self) -> None:
        central = QWidget(self)
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._nav = LeftNavigationBar(central)
        root.addWidget(self._nav)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        self._device_bar = DeviceStatusBar(central)
        right.addWidget(self._device_bar)

        self._page_stack = QStackedWidget(central)
        self._page_stack.setObjectName("pageStack")

        self._scan_page = ScanPage(central)
        self._device_page = DevicePage(central)
        self._analysis_page = AnalysisPage(central)
        self._report_page = ReportPage(central)

        for page in (
            self._scan_page,
            self._device_page,
            self._analysis_page,
            self._report_page,
        ):
            self._page_stack.addWidget(page)

        right.addWidget(self._page_stack, stretch=1)
        root.addLayout(right, stretch=1)

        self._nav.page_changed.connect(self._switch_page)
        self._device_page.action_triggered.connect(self._device_action)

    def _build_docks(self) -> None:
        self._scan_dock = ScanParameterDock(self)
        self._device_dock = DeviceConfigDock(self)
        self._analysis_dock = AnalysisParameterDock(self)
        self._report_dock = ReportSettingsDock(self)

        self._page_docks = [
            self._scan_dock,
            self._device_dock,
            self._analysis_dock,
            self._report_dock,
        ]
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._scan_dock)
        for dock in self._page_docks[1:]:
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
            self.tabifyDockWidget(self._scan_dock, dock)
        self._scan_dock.raise_()
        for dock in self._page_docks:
            dock.setVisible(False)
        for tab_bar in self.findChildren(QTabBar):
            tab_bar.setVisible(False)

        for obj_name, title in (
            ("logDock", "日志"),
            ("spectrumDock", "频谱"),
            ("statisticsDock", "统计"),
        ):
            inner = QWidget()
            inner.setObjectName(f"{obj_name}Content")
            dock = QDockWidget(title, self)
            dock.setObjectName(obj_name)
            dock.setWidget(inner)
            dock.setVisible(False)
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
            self._hidden_docks.append(dock)

    def _current_dock(self) -> QDockWidget:
        return self._page_docks[self._current_page]

    def _switch_page(self, page_index: int) -> None:
        self._current_page = page_index
        self._page_stack.setCurrentIndex(page_index)
        self._rebuild_toolbar(page_index)
        self._status.apply_page(page_index)

        for dock in self._page_docks:
            dock.setVisible(False)

        dock = self._current_dock()
        dock.setVisible(self._action_param_panel.isChecked())
        dock.raise_()
        self._sync_param_action(dock.isVisible())

    def _wire_view_menu(self) -> None:
        self._action_param_panel.triggered.connect(self._toggle_param_dock)
        for dock in self._page_docks:
            dock.visibilityChanged.connect(self._on_dock_visibility_changed)

    def _toggle_param_dock(self, checked: bool) -> None:
        self._current_dock().setVisible(checked)

    def _on_dock_visibility_changed(self, visible: bool) -> None:
        sender = self.sender()
        if sender is self._current_dock():
            self._sync_param_action(visible)

    def _sync_param_action(self, visible: bool) -> None:
        self._action_param_panel.blockSignals(True)
        self._action_param_panel.setChecked(visible)
        self._action_param_panel.blockSignals(False)

    def _device_action(self, text: str) -> None:
        self._status.set_state(f"设备操作：{text}（原型）")

    def _mock_file_action(self) -> None:
        action = self.sender()
        if isinstance(action, QAction):
            self._show_mock(action.text())

    def _toolbar_action(self, log_msg: str, state_msg: str | None):
        def handler(*_args) -> None:
            print(f"[Mock UI] {log_msg}", flush=True)
            if state_msg is not None:
                self._status.set_state(state_msg)

        return handler

    def _mock_log(self, message: str):
        def handler(*_args) -> None:
            print(f"[Mock UI] {message}", flush=True)

        return handler

    def _show_mock(self, message: str) -> None:
        print(f"[Mock UI] {message}", flush=True)
        QMessageBox.information(self, "原型占位", f"{message}\n\n（原型占位，无真实业务）")


def load_stylesheet(app) -> None:
    qss_path = (
        Path(__file__).resolve().parent.parent / "resources" / "styles" / "dark_theme.qss"
    )
    if qss_path.is_file():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
