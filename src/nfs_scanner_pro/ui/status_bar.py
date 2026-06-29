"""底部状态栏 — 消息、进度条、扫描统计、日期时间。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QProgressBar, QStatusBar, QWidget

from nfs_scanner_pro.ui import mock_data


class AppStatusBar:
    """封装 QStatusBar 子控件，供主窗口与工具栏 Mock 更新。"""

    def __init__(self, main_window: QMainWindow) -> None:
        sb = QStatusBar(main_window)
        sb.setObjectName("statusBar")
        main_window.setStatusBar(sb)
        self._bar = sb

        data = mock_data.STATUS_BAR
        self._message = QLabel(f"状态：{data['state']}", main_window)
        self._message.setObjectName("statusBarMessageLabel")
        sb.addWidget(self._message)

        progress_wrap = QWidget(main_window)
        progress_wrap.setObjectName("statusBarProgressWrap")
        from PySide6.QtWidgets import QHBoxLayout

        layout = QHBoxLayout(progress_wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._progress_label = QLabel("扫描进度：0%", main_window)
        self._progress_label.setObjectName("statusBarProgressLabel")
        layout.addWidget(self._progress_label)

        self._progress_bar = QProgressBar(main_window)
        self._progress_bar.setObjectName("statusBarProgressBar")
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(int(data["progress"]))
        self._progress_bar.setFixedWidth(120)
        self._progress_bar.setTextVisible(False)
        layout.addWidget(self._progress_bar)

        sb.addWidget(progress_wrap)

        self._points = QLabel(f"扫描点：{data['points']}", main_window)
        self._points.setObjectName("statusBarPointsLabel")
        sb.addWidget(self._points)

        self._remaining = QLabel(f"预计剩余时间：{data['remaining']}", main_window)
        self._remaining.setObjectName("statusBarRemainingLabel")
        sb.addWidget(self._remaining)

        self._datetime = QLabel(
            f"日期：{data['date']}    时间：{data['time']}",
            main_window,
        )
        self._datetime.setObjectName("statusBarDateTimeLabel")
        self._datetime.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        sb.addPermanentWidget(self._datetime)

    def set_state(self, text: str) -> None:
        self._message.setText(f"状态：{text}")

    def set_progress(self, percent: int) -> None:
        percent = max(0, min(100, percent))
        self._progress_bar.setValue(percent)
        self._progress_label.setText(f"扫描进度：{percent}%")

    @property
    def widget(self) -> QStatusBar:
        return self._bar
