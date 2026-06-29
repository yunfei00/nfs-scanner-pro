"""自定义窗口控制按钮 — 最小化 / 最大化 / 关闭。"""

from __future__ import annotations

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QPushButton, QWidget


class WindowControls(QWidget):
    def __init__(self, window: QMainWindow, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("windowControls")
        self.setFixedHeight(32)
        self._window = window

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(0)

        self._min_btn = QPushButton("—", self)
        self._min_btn.setObjectName("windowMinimizeButton")
        self._min_btn.setToolTip("最小化")
        self._min_btn.setFixedSize(40, 32)
        self._min_btn.clicked.connect(window.showMinimized)

        self._max_btn = QPushButton("□", self)
        self._max_btn.setObjectName("windowMaximizeButton")
        self._max_btn.setToolTip("最大化")
        self._max_btn.setFixedSize(40, 32)
        self._max_btn.clicked.connect(self.toggle_maximize)

        self._close_btn = QPushButton("×", self)
        self._close_btn.setObjectName("windowCloseButton")
        self._close_btn.setToolTip("关闭")
        self._close_btn.setFixedSize(40, 32)
        self._close_btn.clicked.connect(window.close)

        layout.addWidget(self._min_btn)
        layout.addWidget(self._max_btn)
        layout.addWidget(self._close_btn)

        window.installEventFilter(self)
        self.sync_maximize_button()

    def toggle_maximize(self) -> None:
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()
        self.sync_maximize_button()

    def sync_maximize_button(self) -> None:
        if self._window.isMaximized():
            self._max_btn.setText("❐")
            self._max_btn.setToolTip("还原")
        else:
            self._max_btn.setText("□")
            self._max_btn.setToolTip("最大化")

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if obj is self._window and event.type() == QEvent.Type.WindowStateChange:
            self.sync_maximize_button()
        return super().eventFilter(obj, event)
