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
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui.analysis_parameter_dock import AnalysisParameterPanel
from nfs_scanner_pro.ui.device_config_dock import DeviceConfigPanel
from nfs_scanner_pro.ui.device_status_bar import DeviceStatusBar
from nfs_scanner_pro.ui.navigation_bar import LeftNavigationBar
from nfs_scanner_pro.ui.pages.analysis_page import AnalysisPage
from nfs_scanner_pro.ui.pages.device_page import DevicePage
from nfs_scanner_pro.ui.pages.report_page import ReportPage
from nfs_scanner_pro.ui.pages.scan_page import ScanPage
from nfs_scanner_pro.ui.report_settings_dock import ReportSettingsPanel
from nfs_scanner_pro.ui.scan_parameter_dock import ScanParameterPanel, apply_dock_width_policy
from nfs_scanner_pro.ui.scan_state import ScanState
from nfs_scanner_pro.ui.widgets.status_bar import AppStatusBar
from nfs_scanner_pro.ui.widgets.top_menu_bar import TopMenuBar

_SCAN_TOOLBAR = (
    ("toolbarStartScanButton", "开始扫描", "primary", "开始扫描"),
    ("toolbarStopScanButton", "停止扫描", "danger", "停止扫描"),
    ("toolbarCaptureButton", "拍照", "secondary", "拍照"),
    ("toolbarAlignButton", "区域对齐", "secondary", "区域对齐"),
    ("toolbarGridButton", "网格", "secondary", "网格"),
    ("toolbarMeasureButton", "测量", "secondary", "测量"),
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
        self._right_dock: QDockWidget | None = None
        self._dock_stack: QStackedWidget | None = None
        self._page_panels: list[QWidget] = []

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
        self._scan_start_btn: QToolButton | None = None
        self._scan_stop_btn: QToolButton | None = None
        self._rebuild_toolbar(self.PAGE_SCAN)
        self._scan_page.bind_parameter_dock(self._scan_panel)
        self._scan_page.scan_state_changed.connect(self._on_scan_state_changed)
        self._scan_page.scan_status_updated.connect(self._on_scan_status_updated)
        self._analysis_page.analysis_status_updated.connect(self._on_analysis_status_updated)
        self._switch_page(self.PAGE_SCAN)
        self._sync_scan_toolbar()

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
        self._scan_start_btn = None
        self._scan_stop_btn = None
        spec = _REPORT_TOOLBAR if page_index == self.PAGE_REPORT else _SCAN_TOOLBAR
        for index, item in enumerate(spec):
            obj_name, text, variant, log_msg = item[0], item[1], item[2], item[3]
            btn = QToolButton(self)
            btn.setObjectName(obj_name)
            btn.setText(text)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            btn.setProperty("variant", variant)
            btn.setFixedHeight(36)
            if obj_name == "toolbarStartScanButton":
                btn.clicked.connect(self._on_start_scan)
                self._scan_start_btn = btn
            elif obj_name == "toolbarStopScanButton":
                btn.clicked.connect(self._on_stop_scan)
                self._scan_stop_btn = btn
            elif obj_name == "toolbarCaptureButton":
                btn.clicked.connect(self._on_toolbar_capture)
            elif obj_name == "toolbarAlignButton":
                btn.clicked.connect(self._on_toolbar_align)
            elif obj_name == "toolbarGridButton":
                btn.clicked.connect(self._on_toolbar_grid)
            elif obj_name == "toolbarMeasureButton":
                btn.clicked.connect(self._on_toolbar_measure)
            else:
                btn.clicked.connect(self._toolbar_action(log_msg))
            self._tool_bar.addWidget(btn)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            if index == 1:
                self._tool_bar.addSeparator()
        if page_index != self.PAGE_REPORT:
            self._sync_scan_toolbar()

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

    _PAGE_DOCK_TITLES = ("扫描参数", "设备配置", "分析参数", "报告设置")

    def _build_docks(self) -> None:
        self._dock_stack = QStackedWidget(self)
        self._dock_stack.setObjectName("rightDockStack")

        self._scan_panel = ScanParameterPanel(self._dock_stack)
        self._device_panel = DeviceConfigPanel(self._dock_stack)
        self._analysis_panel = AnalysisParameterPanel(self._dock_stack)
        self._report_panel = ReportSettingsPanel(self._dock_stack)
        self._analysis_page.bind_control_panel(self._analysis_panel.control_panel)

        self._page_panels = [
            self._scan_panel,
            self._device_panel,
            self._analysis_panel,
            self._report_panel,
        ]
        for panel in self._page_panels:
            self._dock_stack.addWidget(panel)

        self._right_dock = QDockWidget(self._PAGE_DOCK_TITLES[0], self)
        self._right_dock.setObjectName("rightDock")
        apply_dock_width_policy(self._right_dock)
        self._right_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self._right_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self._right_dock.setFloating(False)
        self._right_dock.setWidget(self._dock_stack)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._right_dock)
        self._mount_page_dock(self.PAGE_SCAN)
        self._validate_single_right_dock()

    def _mount_page_dock(self, page_index: int) -> None:
        """单一 right_dock + 内部 QStackedWidget，不 detach 旧 widget。"""
        if self._right_dock is None or self._dock_stack is None:
            return

        title = self._PAGE_DOCK_TITLES[page_index]
        self._right_dock.setWindowTitle(title)
        self._right_dock.setProperty(
            "dockPage", ("scan", "device", "analysis", "report")[page_index]
        )
        self._right_dock.style().unpolish(self._right_dock)
        self._right_dock.style().polish(self._right_dock)

        self._dock_stack.setCurrentIndex(page_index)

        self._right_dock.setFloating(False)
        self._right_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        if self._action_param_panel.isChecked():
            self._right_dock.show()
        else:
            self._right_dock.hide()

        self._validate_single_right_dock()

    def _validate_single_right_dock(self) -> None:
        """运行期 Dock 健康检查 — 异常仅 print，不弹窗。"""
        if self._right_dock is None or self._dock_stack is None:
            print("[DockCheck] ERROR: right_dock or dock_stack is None", flush=True)
            return

        docks = self.findChildren(QDockWidget)
        if len(docks) != 1:
            print(
                f"[DockCheck] ERROR: expected 1 QDockWidget, found {len(docks)}: "
                f"{[d.objectName() or d.windowTitle() for d in docks]}",
                flush=True,
            )
        elif docks[0] is not self._right_dock:
            print("[DockCheck] ERROR: sole QDockWidget is not right_dock", flush=True)

        if self._right_dock.isFloating():
            print("[DockCheck] ERROR: right_dock is floating — forcing docked", flush=True)
            self._right_dock.setFloating(False)

        expected = self._page_panels[self._current_page]
        if self._dock_stack.currentWidget() is not expected:
            print(
                "[DockCheck] ERROR: dock stack widget does not match current page",
                flush=True,
            )

        for panel in self._page_panels:
            if panel.parent() is not self._dock_stack:
                print(
                    f"[DockCheck] ERROR: panel {panel.objectName()} parent is not dock_stack",
                    flush=True,
                )
            flags = int(panel.windowFlags())
            if flags & int(Qt.WindowType.Window):
                print(
                    f"[DockCheck] ERROR: panel {panel.objectName()} has Window flag",
                    flush=True,
                )

        for w in self.findChildren(QWidget):
            if w is self or w.window() is self:
                continue
            if w.isWindow() and w.parent() is None:
                print(
                    f"[DockCheck] ERROR: orphan top-level widget "
                    f"{w.objectName() or type(w).__name__}",
                    flush=True,
                )

    def _switch_page(self, page_index: int) -> None:
        self._current_page = page_index
        self._page_stack.setCurrentIndex(page_index)
        nav_btn = self._nav._group.button(page_index)
        if nav_btn is not None and not nav_btn.isChecked():
            nav_btn.setChecked(True)
        self._rebuild_toolbar(page_index)
        self._status.apply_page(page_index)
        if page_index == self.PAGE_ANALYSIS:
            self._status._progress_wrap.setVisible(False)
        self._mount_page_dock(page_index)
        if self._right_dock is not None:
            self._sync_param_action(self._right_dock.isVisible())

    def _wire_view_menu(self) -> None:
        self._action_param_panel.triggered.connect(self._toggle_param_dock)
        if self._right_dock is not None:
            self._right_dock.visibilityChanged.connect(self._on_dock_visibility_changed)

    def _toggle_param_dock(self, checked: bool) -> None:
        if self._right_dock is not None:
            self._right_dock.setVisible(checked)
            self._right_dock.setFloating(False)

    def _on_dock_visibility_changed(self, visible: bool) -> None:
        if self.sender() is self._right_dock:
            self._sync_param_action(visible)

    def _sync_param_action(self, visible: bool) -> None:
        self._action_param_panel.blockSignals(True)
        self._action_param_panel.setChecked(visible)
        self._action_param_panel.blockSignals(False)

    def _device_action(self, text: str) -> None:
        self._status.set_state(f"设备操作：{text}（原型）")

    def _on_start_scan(self) -> None:
        print("[Mock UI] 开始扫描", flush=True)
        if self._current_page != self.PAGE_SCAN:
            self._status.set_state("请切换到扫描页后开始扫描")
            return
        self._scan_page.start_scan_mock()

    def _on_stop_scan(self) -> None:
        print("[Mock UI] 停止扫描", flush=True)
        if self._current_page == self.PAGE_ANALYSIS:
            self._status.set_state("当前不在扫描中")
            return
        if self._current_page != self.PAGE_SCAN:
            self._status.set_state("请切换到扫描页后停止扫描")
            return
        self._scan_page.stop_scan_mock()

    def _on_toolbar_capture(self) -> None:
        print("[Mock UI] 拍照", flush=True)
        if self._current_page == self.PAGE_ANALYSIS:
            self._status.set_state("Mock：分析页不执行拍照")
            return
        self._status.set_state("Mock：拍照（原型）")

    def _on_toolbar_align(self) -> None:
        print("[Mock UI] 区域对齐", flush=True)
        if self._current_page == self.PAGE_ANALYSIS:
            self._status.set_state("请切换到扫描页进行区域对齐")
            return
        self._status.set_state("Mock：区域对齐（原型）")

    def _on_toolbar_grid(self) -> None:
        print("[Mock UI] 网格", flush=True)
        if self._current_page == self.PAGE_ANALYSIS:
            visible = self._analysis_page.toggle_grid()
            self._status.set_state(f"Mock：网格{'显示' if visible else '隐藏'}")
            return
        self._status.set_state("Mock：网格切换（原型）")

    def _on_toolbar_measure(self) -> None:
        print("[Mock UI] 测量", flush=True)
        self._status.set_state("Mock：测量工具已启用")

    def _on_analysis_status_updated(
        self, state_text: str, extra1: str, extra2: str
    ) -> None:
        if self._current_page != self.PAGE_ANALYSIS:
            return
        self._status.set_state(state_text)
        self._status._extra1.setText(extra1)
        self._status._extra2.setText(extra2)
        self._status._extra1.setVisible(bool(extra1))
        self._status._extra2.setVisible(bool(extra2))
        self._status._progress_wrap.setVisible(False)

    def _on_scan_state_changed(self, state: ScanState) -> None:
        self._sync_scan_toolbar()

    def _on_scan_status_updated(
        self, state_text: str, progress: int, extra1: str, extra2: str
    ) -> None:
        if self._current_page != self.PAGE_SCAN:
            return
        self._status.set_state(state_text)
        self._status.set_progress(progress)
        self._status._extra1.setText(extra1)
        self._status._extra2.setText(extra2)
        self._status._extra1.setVisible(bool(extra1))
        self._status._extra2.setVisible(bool(extra2))

    def _sync_scan_toolbar(self) -> None:
        if self._scan_start_btn is None or self._scan_stop_btn is None:
            return
        state = self._scan_page.current_scan_state()
        self._scan_start_btn.setEnabled(state.start_enabled())
        self._scan_stop_btn.setEnabled(state.stop_enabled())

    def _toolbar_action(self, log_msg: str):
        def handler(*_args) -> None:
            print(f"[Mock UI] {log_msg}", flush=True)

        return handler

    def _mock_file_action(self) -> None:
        action = self.sender()
        if isinstance(action, QAction):
            self._show_mock(action.text())

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
