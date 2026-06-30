"""设备配置 Dock 内容面板。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.widgets.form_widgets import placeholder_group


class DeviceProfilePanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("deviceProfilePanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        layout.addWidget(self._build_profile_group())
        layout.addWidget(self._build_policy_group())
        layout.addWidget(self._build_safety_group())
        layout.addWidget(
            placeholder_group("高级", "deviceAdvancedGroup", self)
        )
        layout.addStretch()

    def _build_profile_group(self) -> QGroupBox:
        group = QGroupBox("DeviceProfile", self)
        group.setObjectName("deviceProfileGroup")
        form = QFormLayout(group)
        form.setSpacing(8)
        profile = mock_data.DEVICE_PROFILE

        for label, value in (
            ("配置文件", profile["name"]),
            ("运动平台驱动", profile["motion"]),
            ("频谱仪驱动", profile["spectrum"]),
            ("相机驱动", profile["camera"]),
            ("舵机配置", profile["servo"]),
        ):
            field = QLineEdit(value, group)
            field.setReadOnly(True)
            form.addRow(label, field)
        return group

    def _build_policy_group(self) -> QGroupBox:
        group = QGroupBox("连接策略", self)
        group.setObjectName("devicePolicyGroup")
        pl = QVBoxLayout(group)
        policy = mock_data.DEVICE_POLICY
        for text, checked in (
            ("启动时自动连接", policy["auto_connect"]),
            ("相机可选", policy["camera_optional"]),
            ("设备异常时阻止扫描", policy["block_scan_on_fault"]),
        ):
            cb = QCheckBox(text, group)
            cb.setChecked(checked)
            cb.setEnabled(False)
            pl.addWidget(cb)
        return group

    def _build_safety_group(self) -> QGroupBox:
        group = QGroupBox("安全限制", self)
        group.setObjectName("deviceSafetyGroup")
        form = QFormLayout(group)
        safety = mock_data.DEVICE_SAFETY
        for label, value in (
            ("X 范围", safety["x_range"]),
            ("Y 范围", safety["y_range"]),
            ("Z 范围", safety["z_range"]),
            ("默认速度", safety["default_speed"]),
        ):
            field = QLineEdit(value, group)
            field.setReadOnly(True)
            form.addRow(label, field)
        return group
