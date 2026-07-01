"""顶部区域 — 标题栏 + 固定菜单栏 + 窗口控制。"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QMenuBar, QSizePolicy, QVBoxLayout, QWidget

from nfs_scanner_pro.ui.widgets.window_controls import WindowControls

TITLE_BAR_HEIGHT = 32
MENU_BAR_HEIGHT = 32


class TopMenuBar(QWidget):
    def __init__(self, window: QMainWindow, menu_bar: QMenuBar, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("topMenuBar")
        self.setFixedHeight(TITLE_BAR_HEIGHT + MENU_BAR_HEIGHT)
        self._window = window
        self._menu_bar = menu_bar
        self._drag_offset: QPoint | None = None
        self._drag_from_maximized = False
        self._drag_ratio_x = 0.5

        menu_bar.setNativeMenuBar(False)
        menu_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        menu_bar.setFixedHeight(MENU_BAR_HEIGHT)

        self._title_strip = QWidget(self)
        self._title_strip.setObjectName("titleBarStrip")
        self._title_strip.setFixedHeight(TITLE_BAR_HEIGHT)
        title_layout = QHBoxLayout(self._title_strip)
        title_layout.setContentsMargins(12, 0, 0, 0)
        title_layout.setSpacing(0)

        self._title_label = QLabel(window.windowTitle(), self._title_strip)
        self._title_label.setObjectName("titleBarLabel")
        title_layout.addWidget(self._title_label)
        title_layout.addStretch(1)

        self._controls = WindowControls(window, self._title_strip)
        title_layout.addWidget(self._controls)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._title_strip)
        layout.addWidget(menu_bar)

        self._title_strip.installEventFilter(self)
        self._title_label.installEventFilter(self)

    def set_title_text(self, text: str) -> None:
        self._title_label.setText(text)

    def _start_drag(self, global_pos: QPoint) -> None:
        geometry = self._window.frameGeometry()
        self._drag_from_maximized = self._window.isMaximized()
        if self._drag_from_maximized:
            self._drag_ratio_x = (
                (global_pos.x() - geometry.left()) / max(1, geometry.width())
            )
            self._drag_offset = QPoint(0, max(1, TITLE_BAR_HEIGHT // 2))
            return
        self._drag_offset = global_pos - geometry.topLeft()

    def _perform_drag(self, global_pos: QPoint) -> None:
        if self._drag_offset is None:
            return
        if self._drag_from_maximized:
            self._window.showNormal()
            restored_width = max(1, self._window.frameGeometry().width())
            self._drag_offset = QPoint(
                int(restored_width * self._drag_ratio_x),
                max(1, TITLE_BAR_HEIGHT // 2),
            )
            self._drag_from_maximized = False
        self._window.move(global_pos - self._drag_offset)

    def _end_drag(self) -> None:
        self._drag_offset = None
        self._drag_from_maximized = False

    def _handle_title_mouse_press(self, event: QMouseEvent) -> bool:
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        self._start_drag(event.globalPosition().toPoint())
        return True

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if obj in (self._title_strip, self._title_label):
            et = event.type()
            if et == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent):
                if self._handle_title_mouse_press(event):
                    return True
            if et == QEvent.Type.MouseMove and isinstance(event, QMouseEvent):
                if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
                    self._perform_drag(event.globalPosition().toPoint())
                    return True
            if et == QEvent.Type.MouseButtonRelease:
                self._end_drag()
            if et == QEvent.Type.MouseButtonDblClick and isinstance(event, QMouseEvent):
                if event.button() == Qt.MouseButton.LeftButton:
                    self._end_drag()
                    self._controls.toggle_maximize()
                    return True
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self.childAt(event.pos()) is self._menu_bar:
            super().mousePressEvent(event)
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._perform_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._end_drag()
        super().mouseReleaseEvent(event)
