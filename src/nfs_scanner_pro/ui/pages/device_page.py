"""设备页 — 四设备卡片。"""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.widgets.section_card import DeviceCard, JogPad, ServoSelector


class DevicePage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("devicePage")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        crumb = QLabel(f"设备中心 > {mock_data.DEVICE_PROFILE} > 四设备联机配置", self)
        crumb.setObjectName("breadcrumbBar")
        crumb.setProperty("role", "pageBreadcrumb")
        root.addWidget(crumb)

        grid_wrap = QWidget(self)
        grid_wrap.setObjectName("deviceCenter")
        grid = QGridLayout(grid_wrap)
        grid.setContentsMargins(16, 16, 16, 16)
        grid.setSpacing(16)

        pos = mock_data.POSITION
        motion = DeviceCard(
            "运动平台",
            [
                ("端口", "COM6"),
                ("波特率", "115200"),
                ("状态", "已连接"),
                ("当前坐标", f"X {pos['x']:.2f} / Y {pos['y']:.2f} / Z {pos['z']:.2f} mm"),
            ],
            [("motionHomeButton", "回零")],
            extra=JogPad(grid_wrap),
        )
        motion.setObjectName("deviceCardMotion")
        motion.action_clicked.connect(self._on_action)

        spectrum = DeviceCard(
            "频谱仪",
            [
                ("型号", "ZNA67"),
                ("连接方式", "TCP/IP"),
                ("地址", "192.168.1.100:5025"),
                ("Trace", "Trace 1"),
                ("频率范围", "1 MHz — 67 GHz"),
            ],
            [("spectrumTestButton", "测试连接")],
        )
        spectrum.setObjectName("deviceCardSpectrum")
        spectrum.action_clicked.connect(self._on_action)

        preview = QLabel("相机预览区域（Mock）", grid_wrap)
        preview.setObjectName("cameraPreview")
        preview.setProperty("role", "cameraPreview")
        preview.setMinimumHeight(100)
        camera = DeviceCard(
            "相机",
            [
                ("接口", "USB3.0"),
                ("分辨率", "4096 × 3000"),
                ("状态", "预览就绪"),
            ],
            [("cameraCaptureButton", "拍照")],
            extra=preview,
        )
        camera.setObjectName("deviceCardCamera")
        camera.action_clicked.connect(self._on_action)

        servo_extra = QWidget(grid_wrap)
        sl = QVBoxLayout(servo_extra)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.addWidget(ServoSelector(servo_extra))
        servo = DeviceCard(
            "舵机系统",
            [
                ("旋转角度", "0.0°"),
                ("偏移补偿", "X +0.02 / Y -0.01 mm"),
            ],
            [("servoCalibrateButton", "Hx/Hy 校准")],
            extra=servo_extra,
        )
        servo.setObjectName("deviceCardServo")
        servo.action_clicked.connect(self._on_action)

        grid.addWidget(motion, 0, 0)
        grid.addWidget(spectrum, 0, 1)
        grid.addWidget(camera, 1, 0)
        grid.addWidget(servo, 1, 1)
        root.addWidget(grid_wrap, stretch=1)

        self.action_triggered = motion.action_clicked

    def _on_action(self, text: str) -> None:
        print(f"[Mock UI] 设备操作：{text}", flush=True)
