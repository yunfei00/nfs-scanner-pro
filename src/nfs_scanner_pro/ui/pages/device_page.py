"""设备页 — Device Center Mock（Release 012）。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.widgets.camera_preview_mock import CameraPreviewMock
from nfs_scanner_pro.ui.widgets.device_card import DeviceCard
from nfs_scanner_pro.ui.widgets.hxhy_control import HxHyControl
from nfs_scanner_pro.ui.widgets.jog_control import JogControl

_MOCK_STATUS: dict[str, str] = {
    "回零": "运动平台回零命令已触发",
    "停止": "运动平台停止命令已触发",
    "刷新位置": "运动平台位置已刷新",
    "Y+": "运动平台 Jog：Y+",
    "Y-": "运动平台 Jog：Y-",
    "X+": "运动平台 Jog：X+",
    "X-": "运动平台 Jog：X-",
    "Z+": "运动平台 Jog：Z+",
    "Z-": "运动平台 Jog：Z-",
    "●": "运动平台 Jog：中心",
    "测试连接": "频谱仪连接测试成功",
    "单次 Sweep": "频谱仪单次 Sweep 完成",
    "读取 Trace": "频谱仪 Trace 已读取",
    "拍照": "相机拍照完成",
    "刷新预览": "相机预览已刷新",
    "打开相机设置": "相机设置面板已打开（Mock）",
    "切换到 Hx": "已切换到 Hx，等待重新确认对齐",
    "切换到 Hy": "已切换到 Hy，等待重新确认对齐",
    "Hx/Hy 校准": "Hx/Hy 校准流程已启动（Mock）",
    "应用偏移补偿": "偏移补偿已应用（Mock）",
}


class DevicePage(QWidget):
    action_triggered = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("devicePage")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        profile_name = mock_data.DEVICE_PROFILE["name"]
        crumb = QLabel(f"设备中心 > {profile_name} > 四设备联调配置", self)
        crumb.setObjectName("breadcrumbBar")
        crumb.setProperty("role", "pageBreadcrumb")
        root.addWidget(crumb)

        grid_wrap = QWidget(self)
        grid_wrap.setObjectName("deviceCenter")
        grid = QGridLayout(grid_wrap)
        grid.setContentsMargins(16, 16, 16, 16)
        grid.setSpacing(16)

        motion = self._build_motion_card(grid_wrap)
        spectrum = self._build_spectrum_card(grid_wrap)
        camera = self._build_camera_card(grid_wrap)
        servo = self._build_servo_card(grid_wrap)

        grid.addWidget(motion, 0, 0)
        grid.addWidget(spectrum, 0, 1)
        grid.addWidget(camera, 1, 0)
        grid.addWidget(servo, 1, 1)
        root.addWidget(grid_wrap, stretch=1)

    def _build_motion_card(self, parent: QWidget) -> DeviceCard:
        m = mock_data.MOTION_STATE
        jog = JogControl(parent)
        jog.jog_clicked.connect(self._on_mock_action)
        card = DeviceCard(
            "运动平台",
            [
                ("端口", m["port"]),
                ("波特率", str(m["baudrate"])),
                ("状态", m["status"]),
                (
                    "当前坐标",
                    f"X {m['x']:.2f} / Y {m['y']:.2f} / Z {m['z']:.2f} mm",
                ),
                ("行程范围", f"X {m['travel_x']} / Y {m['travel_y']} / Z {m['travel_z']}"),
                ("速度", f"{m['speed']} mm/min"),
            ],
            [
                ("motionHomeButton", "回零", "action"),
                ("motionStopButton", "停止", "danger"),
                ("motionRefreshButton", "刷新位置", "action"),
            ],
            extra=jog,
            object_name="deviceCardMotion",
            parent=parent,
        )
        card.action_clicked.connect(self._on_mock_action)
        return card

    def _build_spectrum_card(self, parent: QWidget) -> DeviceCard:
        s = mock_data.SPECTRUM_STATE
        card = DeviceCard(
            "频谱仪",
            [
                ("型号", s["model"]),
                ("连接方式", s["connection"]),
                ("地址", s["address"]),
                ("Trace", s["trace"]),
                ("频率范围", s["freq_range"]),
                ("当前频率", s["current_freq"]),
            ],
            [
                ("spectrumTestButton", "测试连接", "primary"),
                ("spectrumSweepButton", "单次 Sweep", "action"),
                ("spectrumReadTraceButton", "读取 Trace", "action"),
            ],
            object_name="deviceCardSpectrum",
            parent=parent,
        )
        card.action_clicked.connect(self._on_mock_action)
        return card

    def _build_camera_card(self, parent: QWidget) -> DeviceCard:
        c = mock_data.CAMERA_STATE
        preview = CameraPreviewMock(parent)
        card = DeviceCard(
            "相机",
            [
                ("接口", c["interface"]),
                ("分辨率", c["resolution"]),
                ("状态", c["status"]),
                (
                    "拍照位置",
                    f"X {c['capture_x']:.0f} / Y {c['capture_y']:.0f} / Z {c['capture_z']:.2f}",
                ),
            ],
            [
                ("cameraCaptureButton", "拍照", "primary"),
                ("cameraRefreshButton", "刷新预览", "action"),
                ("cameraSettingsButton", "打开相机设置", "action"),
            ],
            extra=preview,
            object_name="deviceCardCamera",
            parent=parent,
        )
        card.action_clicked.connect(self._on_mock_action)
        return card

    def _build_servo_card(self, parent: QWidget) -> DeviceCard:
        s = mock_data.SERVO_STATE
        hxhy = HxHyControl(current=s["current_probe"], parent=parent)
        hxhy.action_clicked.connect(self._on_servo_action)
        card = DeviceCard(
            "舵机系统",
            [
                ("当前探头", s["current_probe"]),
                ("Hy 状态", s["hy_status"]),
                ("旋转角度", s["angle"]),
                ("偏移补偿", s["offset"]),
                ("校准状态", s["calibration"]),
            ],
            actions=[],
            extra=hxhy,
            object_name="deviceCardServo",
            parent=parent,
        )
        self._hxhy = hxhy
        return card

    def _on_servo_action(self, action: str) -> None:
        if action == "切换到 Hx":
            self._hxhy.set_probe("Hx")
        elif action == "切换到 Hy":
            self._hxhy.set_probe("Hy")
        self._on_mock_action(action)

    def _on_mock_action(self, action: str) -> None:
        message = _MOCK_STATUS.get(action, f"设备操作：{action}")
        print(f"[Mock UI] {message}", flush=True)
        win = self.window()
        status = getattr(win, "_status", None)
        if status is not None:
            status.set_state(f"Mock：{message}")
