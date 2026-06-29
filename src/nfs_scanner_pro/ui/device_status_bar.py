"""设备状态栏 — 单行展示四设备与扫描上下文。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from nfs_scanner_pro.ui import mock_data


class DeviceStatusBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("deviceStatusBar")
        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        indicator_names = [
            "deviceStatusMotionIndicator",
            "deviceStatusSpectrumIndicator",
            "deviceStatusCameraIndicator",
            "deviceStatusServoIndicator",
        ]

        for device, obj_name in zip(mock_data.DEVICE_STATUS, indicator_names):
            detail = f"({device['detail']})" if device["detail"] else ""
            label = QLabel(f"● {device['name']}{detail}", self)
            label.setObjectName(obj_name)
            label.setProperty("status", device["status"])
            tooltip = mock_data.DEVICE_TOOLTIPS.get(device["name"], device["name"])
            label.setToolTip(tooltip)
            layout.addWidget(label)

        sep = QLabel("|", self)
        sep.setObjectName("deviceStatusSeparator")
        layout.addWidget(sep)

        meta_parts = [
            f"探头：{mock_data.PROBE_NAME}",
            f"高度：{mock_data.POSITION['z']:.3f} mm",
            f"区域：{mock_data.REGION_NAME}",
            f"频率：{mock_data.FREQUENCY}",
            f"点数：{mock_data.POINTS}",
        ]
        meta = QLabel("  |  ".join(meta_parts), self)
        meta.setObjectName("deviceStatusMetaLabel")
        meta.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(meta, stretch=1)
