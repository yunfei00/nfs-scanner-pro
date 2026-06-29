"""主窗口 — Release 010 Mock 壳层。"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui.device_status_bar import DeviceStatusBar
from nfs_scanner_pro.ui.mock_data import STATUS_BAR
from nfs_scanner_pro.ui.navigation_bar import LeftNavigationBar
from nfs_scanner_pro.ui.scan_canvas_view import ScanCanvasWidget
from nfs_scanner_pro.ui.scan_parameter_dock import ScanParameterDock


class MainWindow(QMainWindow):
    WINDOW_TITLE = "近场扫描系统"
    DEFAULT_WIDTH = 1600
    DEFAULT_HEIGHT = 1000

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        self._hidden_docks: list[QDockWidget] = []
        self._build_menu_bar()
        self._build_tool_bar()
        self._build_central()
        self._build_docks()
        self._build_status_bar()
        self._wire_view_menu()

    def _build_menu_bar(self) -> None:
        mb = self.menuBar()
        mb.setObjectName("menuBar")

        file_menu = mb.addMenu("文件(&F)")
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

        mb.addMenu("编辑(&E)")
        view_menu = mb.addMenu("视图(&V)")

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

        mb.addMenu("工具(&T)")
        mb.addMenu("设置(&S)")
        mb.addMenu("帮助(&H)")

    def _build_tool_bar(self) -> None:
        tb = QToolBar("主工具栏", self)
        tb.setObjectName("mainToolBar")
        tb.setMovable(False)
        self.addToolBar(tb)

        buttons = (
            ("toolbarStartScanButton", "开始扫描", "primary", "开始扫描"),
            ("toolbarStopScanButton", "停止扫描", "danger", "停止扫描"),
            ("toolbarCaptureButton", "拍照", "secondary", "拍照"),
            ("toolbarAlignButton", "区域对齐", "secondary", "区域对齐"),
            ("toolbarGridButton", "网格", "secondary", "网格"),
            ("toolbarMeasureButton", "测量", "secondary", "测量"),
        )
        for obj_name, text, variant, log_msg in buttons:
            btn = QToolButton(self)
            btn.setObjectName(obj_name)
            btn.setText(text)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            btn.setProperty("variant", variant)
            btn.clicked.connect(self._mock_log(log_msg))
            tb.addWidget(btn)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

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

        self._scan_page = ScanCanvasWidget(central)
        self._page_stack.addWidget(self._scan_page)

        for obj_name, title in (
            ("devicePage", "设备"),
            ("analysisPage", "分析"),
            ("reportPage", "报告"),
        ):
            page = QLabel(f"{title}模块（Mock 占位）", central)
            page.setObjectName(obj_name)
            page.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._page_stack.addWidget(page)

        right.addWidget(self._page_stack, stretch=1)
        root.addLayout(right, stretch=1)

        self._nav.page_changed.connect(self._page_stack.setCurrentIndex)

    def _build_docks(self) -> None:
        self._param_dock = ScanParameterDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._param_dock)

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

    def _build_status_bar(self) -> None:
        sb = QStatusBar(self)
        sb.setObjectName("statusBar")
        self.setStatusBar(sb)

        msg = QLabel(f"状态：{STATUS_BAR['state']}", self)
        msg.setObjectName("statusBarMessageLabel")
        sb.addWidget(msg)

        for text, obj in (
            (f"扫描进度：{STATUS_BAR['progress']}", "statusBarProgressLabel"),
            (f"扫描点：{STATUS_BAR['points']}", "statusBarPointsLabel"),
            (f"预计剩余时间：{STATUS_BAR['remaining']}", "statusBarRemainingLabel"),
        ):
            lbl = QLabel(text, self)
            lbl.setObjectName(obj)
            sb.addWidget(lbl)

        dt = QLabel(
            f"日期：{STATUS_BAR['date']}    时间：{STATUS_BAR['time']}",
            self,
        )
        dt.setObjectName("statusBarDateTimeLabel")
        sb.addPermanentWidget(dt)

    def _wire_view_menu(self) -> None:
        self._action_param_panel.triggered.connect(self._toggle_param_dock)
        self._param_dock.visibilityChanged.connect(self._sync_param_action)

    def _toggle_param_dock(self, checked: bool) -> None:
        self._param_dock.setVisible(checked)

    def _sync_param_action(self, visible: bool) -> None:
        self._action_param_panel.blockSignals(True)
        self._action_param_panel.setChecked(visible)
        self._action_param_panel.blockSignals(False)

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
        QMessageBox.information(self, "Mock", f"{message}\n\n（Mock 占位，无真实业务）")


def load_stylesheet(app) -> None:
    qss_path = (
        Path(__file__).resolve().parent.parent / "resources" / "styles" / "dark_theme.qss"
    )
    if qss_path.is_file():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
