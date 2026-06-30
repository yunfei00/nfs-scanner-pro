"""设备配置面板 — QWidget 内容（由 MainWindow 单一 Dock 挂载）。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from nfs_scanner_pro.ui.widgets.device_profile_panel import DeviceProfilePanel


class DeviceConfigPanel(QWidget):
    """设备配置面板 — 非 QDockWidget。"""

    DOCK_WIDTH = 360

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("deviceConfigPanel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("deviceConfigScroll")
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("deviceConfigContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(DeviceProfilePanel(content))

        scroll.setWidget(content)
        outer.addWidget(scroll)


DeviceConfigDock = DeviceConfigPanel
