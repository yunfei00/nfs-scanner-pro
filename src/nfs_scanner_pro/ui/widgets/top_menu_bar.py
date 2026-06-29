"""顶部菜单栏容器 — 菜单 + 窗口控制 + 拖动 / 双击最大化。"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMenuBar, QWidget

from nfs_scanner_pro.ui.widgets.window_controls import WindowControls


class TopMenuBar(QWidget):
    def __init__(self, window: QMainWindow, menu_bar: QMenuBar, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("topMenuBar")
        self.setFixedHeight(32)
        self._window = window
        self._menu_bar = menu_bar
        self._drag_offset: QPoint | None = None
        self._drag_from_maximized = False
        self._drag_ratio_x = 0.5

        menu_bar.setFixedHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(menu_bar, stretch=1)

        self._controls = WindowControls(window, self)
        layout.addWidget(self._controls)

        menu_bar.installEventFilter(self)

    def _menu_bar_drag_ok(self, pos: QPoint) -> bool:
        for action in self._menu_bar.actions():
            if self._menu_bar.actionGeometry(action).contains(pos):
                return False
        return True

    def _start_drag(self, global_pos: QPoint) -> None:
        geometry = self._window.frameGeometry()
        self._drag_from_maximized = self._window.isMaximized()
        if self._drag_from_maximized:
            self._drag_ratio_x = (
                (global_pos.x() - geometry.left()) / max(1, geometry.width())
            )
            self._drag_offset = QPoint(0, max(1, self.height() // 2))
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
                max(1, self.height() // 2),
            )
            self._drag_from_maximized = False
        self._window.move(global_pos - self._drag_offset)

    def _end_drag(self) -> None:
        self._drag_offset = None
        self._drag_from_maximized = False

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if obj is self._menu_bar:
            et = event.type()
            if et == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent):
                if (
                    event.button() == Qt.MouseButton.LeftButton
                    and self._menu_bar_drag_ok(event.pos())
                ):
                    self._start_drag(event.globalPosition().toPoint())
                    return True
            if et == QEvent.Type.MouseMove and isinstance(event, QMouseEvent):
                if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
                    self._perform_drag(event.globalPosition().toPoint())
                    return True
            if et == QEvent.Type.MouseButtonRelease:
                self._end_drag()
            if et == QEvent.Type.MouseButtonDblClick and isinstance(event, QMouseEvent):
                if (
                    event.button() == Qt.MouseButton.LeftButton
                    and self._menu_bar_drag_ok(event.pos())
                ):
                    self._end_drag()
                    self._controls.toggle_maximize()
                    return True
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self.childAt(event.pos()) is None:
            self._start_drag(event.globalPosition().toPoint())
            event.accept()
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

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self.childAt(event.pos()) is None:
            self._end_drag()
            self._controls.toggle_maximize()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
