"""设备配置 Dock。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.scan_parameter_dock import apply_dock_width_policy
from nfs_scanner_pro.ui.widgets.form_widgets import placeholder_group


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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        profile = QGroupBox("设备配置文件", self)
        profile.setObjectName("deviceProfileGroup")
        form = QFormLayout(profile)
        cfg = QLineEdit(mock_data.DEVICE_PROFILE)
        cfg.setReadOnly(True)
        form.addRow("配置文件", cfg)
        motion = QComboBox()
        motion.addItem("COM6 · 115200")
        motion.setEnabled(False)
        form.addRow("运动平台驱动", motion)
        spec = QComboBox()
        spec.addItem("ZNA67 · TCP/IP")
        spec.setEnabled(False)
        form.addRow("频谱仪驱动", spec)
        layout.addWidget(profile)

        policy = QGroupBox("连接策略", self)
        policy.setObjectName("devicePolicyGroup")
        pl = QVBoxLayout(policy)
        cb1 = QCheckBox("启动时自动连接")
        cb1.setChecked(True)
        cb1.setEnabled(False)
        cb2 = QCheckBox("相机可选（离线不阻止扫描）")
        cb2.setChecked(True)
        cb2.setEnabled(False)
        pl.addWidget(cb1)
        pl.addWidget(cb2)
        layout.addWidget(policy)
        layout.addWidget(placeholder_group("高级", "deviceAdvancedGroup", self))
        layout.addStretch()

        scroll.setWidget(content)
        self.setWidget(scroll)
