"""设备配置 Dock。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QScrollArea, QVBoxLayout, QWidget

from nfs_scanner_pro.ui.scan_parameter_dock import apply_dock_width_policy
from nfs_scanner_pro.ui.widgets.device_profile_panel import DeviceProfilePanel


class DeviceConfigDock(QDockWidget):
    DOCK_WIDTH = 360

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("设备配置", parent)
        self.setObjectName("deviceConfigDock")
        apply_dock_width_policy(self)
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

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
        self.setWidget(scroll)
