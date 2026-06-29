"""底部状态栏 — 按页面切换显示配置。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QProgressBar, QStatusBar, QWidget

from nfs_scanner_pro.ui import mock_data


class AppStatusBar:
    PAGE_SCAN = 0
    PAGE_DEVICE = 1
    PAGE_ANALYSIS = 2
    PAGE_REPORT = 3

    def __init__(self, main_window: QMainWindow) -> None:
        sb = QStatusBar(main_window)
        sb.setObjectName("statusBar")
        main_window.setStatusBar(sb)
        self._bar = sb
        self._host = main_window

        self._message = QLabel(main_window)
        self._message.setObjectName("statusBarMessageLabel")

        self._progress_wrap = QWidget(main_window)
        self._progress_wrap.setObjectName("statusBarProgressWrap")
        pw_layout = QHBoxLayout(self._progress_wrap)
        pw_layout.setContentsMargins(0, 0, 0, 0)
        pw_layout.setSpacing(8)
        self._progress_label = QLabel(main_window)
        self._progress_label.setObjectName("statusBarProgressLabel")
        self._progress_bar = QProgressBar(main_window)
        self._progress_bar.setObjectName("statusBarProgressBar")
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setFixedWidth(120)
        self._progress_bar.setTextVisible(False)
        pw_layout.addWidget(self._progress_label)
        pw_layout.addWidget(self._progress_bar)

        self._extra1 = QLabel(main_window)
        self._extra1.setObjectName("statusBarExtra1Label")
        self._extra2 = QLabel(main_window)
        self._extra2.setObjectName("statusBarExtra2Label")
        self._datetime = QLabel(main_window)
        self._datetime.setObjectName("statusBarDateTimeLabel")
        self._datetime.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        sb.addWidget(self._message)
        sb.addWidget(self._progress_wrap)
        sb.addWidget(self._extra1)
        sb.addWidget(self._extra2)
        sb.addPermanentWidget(self._datetime)

        self.apply_page(self.PAGE_SCAN)

    def apply_page(self, page_index: int) -> None:
        profiles = (
            mock_data.STATUS_SCAN,
            mock_data.STATUS_DEVICE,
            mock_data.STATUS_ANALYSIS,
            mock_data.STATUS_REPORT,
        )
        profile = profiles[page_index]
        self._message.setText(f"状态：{profile['state']}")
        self._extra1.setText(profile.get("extra1", ""))
        self._extra2.setText(profile.get("extra2", ""))
        self._extra1.setVisible(bool(profile.get("extra1")))
        self._extra2.setVisible(bool(profile.get("extra2")))
        self._datetime.setText(f"日期：{mock_data.DATE}    时间：{mock_data.TIME}")

        show_progress = page_index == self.PAGE_SCAN
        self._progress_wrap.setVisible(show_progress)
        if show_progress:
            self.set_progress(int(profile.get("progress", 0)))

    def set_state(self, text: str) -> None:
        self._message.setText(f"状态：{text}")

    def set_progress(self, percent: int) -> None:
        percent = max(0, min(100, percent))
        self._progress_bar.setValue(percent)
        self._progress_label.setText(f"扫描进度：{percent}%")

    @property
    def widget(self) -> QStatusBar:
        return self._bar
