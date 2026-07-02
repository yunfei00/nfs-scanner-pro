"""设备页 — Device Center Mock（Release 012/018 / 045 硬件模式）。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.devices import get_device_manager
from nfs_scanner_pro.devices.hardware_mode import (
    HardwareMode,
    get_hardware_mode,
    normalize_hardware_mode,
    set_hardware_mode,
)
from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.widgets.camera_preview_mock import CameraPreviewMock
from nfs_scanner_pro.ui.widgets.device_card import DeviceCard
from nfs_scanner_pro.ui.widgets.hxhy_control import HxHyControl
from nfs_scanner_pro.ui.widgets.jog_control import JogControl


class DevicePage(QWidget):
    action_triggered = Signal(str)
    hardware_mode_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("devicePage")
        self._manager = get_device_manager()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        profile_name = mock_data.DEVICE_PROFILE["name"]
        crumb = QLabel(f"设备中心 > {profile_name} > 四设备联调配置", self)
        crumb.setObjectName("breadcrumbBar")
        crumb.setProperty("role", "pageBreadcrumb")
        root.addWidget(crumb)
        self._build_hardware_mode_bar(root)

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

        for device in (
            self._manager.motion,
            self._manager.spectrum,
            self._manager.camera,
            self._manager.servo,
        ):
            device.add_state_listener(self._on_device_state_changed)

        self._refresh_from_manager()
        self.apply_hardware_mode(get_hardware_mode())

    def _build_hardware_mode_bar(self, root: QVBoxLayout) -> None:
        bar = QWidget(self)
        bar.setObjectName("hardwareModeBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        layout.addWidget(QLabel("硬件模式：", bar))
        self._mode_combo = QComboBox(bar)
        self._mode_combo.setObjectName("hardwareModeCombo")
        for label, value in (
            ("Mock 模式", HardwareMode.MOCK.value),
            ("Fake 模式", HardwareMode.FAKE.value),
            ("Real 模式", HardwareMode.REAL.value),
        ):
            self._mode_combo.addItem(label, value)
        self._mode_combo.currentIndexChanged.connect(self._on_hardware_mode_combo_changed)
        layout.addWidget(self._mode_combo)

        self._probe_btn = QPushButton("安全探测", bar)
        self._probe_btn.setObjectName("realSafeProbeButton")
        self._probe_btn.clicked.connect(self._on_safe_probe)
        self._probe_btn.setVisible(False)
        layout.addWidget(self._probe_btn)

        self._mode_hint = QLabel("", bar)
        self._mode_hint.setObjectName("hardwareModeHint")
        self._mode_hint.setWordWrap(True)
        layout.addWidget(self._mode_hint, stretch=1)
        root.addWidget(bar)

    def apply_hardware_mode(self, mode: str | HardwareMode) -> None:
        normalized = normalize_hardware_mode(mode)
        self._mode_combo.blockSignals(True)
        index = self._mode_combo.findData(normalized.value)
        if index >= 0:
            self._mode_combo.setCurrentIndex(index)
        self._mode_combo.blockSignals(False)
        self._update_hardware_mode_ui(normalized)

    def _on_hardware_mode_combo_changed(self, _index: int) -> None:
        value = self._mode_combo.currentData()
        mode = set_hardware_mode(value)
        self._update_hardware_mode_ui(mode)
        self.hardware_mode_changed.emit(mode.value)

    def _update_hardware_mode_ui(self, mode: HardwareMode) -> None:
        self._probe_btn.setVisible(mode is HardwareMode.REAL)
        if mode is HardwareMode.MOCK:
            self._mode_hint.setText("Mock 模式 — 使用 MockDeviceManager，不连接真实设备。")
        elif mode is HardwareMode.FAKE:
            self._mode_hint.setText(
                "Fake Ready — 已切换到 Fake Hardware 模式，使用 FakeTransport 离线测试，不连接真实设备。"
            )
        else:
            self._mode_hint.setText(
                "Real Hardware 模式已选择，但尚未连接。"
                "如需连接，请设置 NFS_ENABLE_REAL_HARDWARE=1 并点击安全探测。"
            )

    def _on_safe_probe(self) -> None:
        from nfs_scanner_pro.devices.real.hardware_config import is_real_hardware_enabled
        from nfs_scanner_pro.devices.real.real_device_manager import RealDeviceManager

        if not is_real_hardware_enabled():
            message = "真实硬件未启用，请设置 NFS_ENABLE_REAL_HARDWARE=1"
            self._mode_hint.setText(message)
            self._show_result(message)
            return

        manager = RealDeviceManager()
        try:
            result = manager.test_all_safe()
            if result.get("status") == "disabled":
                message = str(result.get("message", "真实硬件未启用"))
                self._mode_hint.setText(message)
                self._show_result(message)
                return
            summary = "；".join(f"{key}={value}" for key, value in sorted(result.items()))
            message = f"安全探测完成：{summary}"
            self._mode_hint.setText("Real Hardware 安全探测已完成（无运动 / 无 sweep）。")
            self._show_result(message)
        finally:
            manager.disconnect_all()

    def _on_device_state_changed(self, _state) -> None:
        self._refresh_from_manager()

    def _build_motion_card(self, parent: QWidget) -> DeviceCard:
        m = self._manager.motion
        jog = JogControl(parent)
        jog.jog_clicked.connect(self._on_jog_action)
        card = DeviceCard(
            "运动平台",
            [
                ("端口", m.port),
                ("波特率", str(m.baudrate)),
                ("状态", m.status_text()),
                (
                    "当前坐标",
                    f"X {m.x:.2f} / Y {m.y:.2f} / Z {m.z:.2f} mm",
                ),
                ("行程范围", f"X {m.travel_x} / Y {m.travel_y} / Z {m.travel_z}"),
                ("速度", f"{m.speed} mm/min"),
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
        card.action_clicked.connect(self._on_card_action)
        self._motion_card = card
        self._motion_status_label = card.findChild(QLabel, "deviceCardValue2")
        self._motion_position_label = card.findChild(QLabel, "deviceCardValue3")
        return card

    def _build_spectrum_card(self, parent: QWidget) -> DeviceCard:
        s = self._manager.spectrum
        card = DeviceCard(
            "频谱仪",
            [
                ("型号", s.model),
                ("连接方式", s.connection),
                ("地址", s.address),
                ("Trace", s.trace),
                ("频率范围", s.freq_range),
                ("当前频率", s.current_freq),
            ],
            [
                ("spectrumTestButton", "测试连接", "primary"),
                ("spectrumSweepButton", "单次 Sweep", "action"),
                ("spectrumReadTraceButton", "读取 Trace", "action"),
            ],
            object_name="deviceCardSpectrum",
            parent=parent,
        )
        card.action_clicked.connect(self._on_card_action)
        return card

    def _build_camera_card(self, parent: QWidget) -> DeviceCard:
        c = self._manager.camera
        preview = CameraPreviewMock(parent)
        card = DeviceCard(
            "相机",
            [
                ("接口", c.interface),
                ("分辨率", c.resolution),
                ("状态", c.status_label),
                (
                    "拍照位置",
                    f"X {c.capture_x:.0f} / Y {c.capture_y:.0f} / Z {c.capture_z:.2f}",
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
        card.action_clicked.connect(self._on_card_action)
        return card

    def _build_servo_card(self, parent: QWidget) -> DeviceCard:
        s = self._manager.servo
        hxhy = HxHyControl(current=s.current_probe, parent=parent)
        hxhy.action_clicked.connect(self._on_servo_action)
        card = DeviceCard(
            "舵机系统",
            [
                ("当前探头", s.current_probe),
                ("Hy 状态", s.hy_status),
                ("旋转角度", s.angle),
                ("偏移补偿", s.offset),
                ("校准状态", s.calibration),
            ],
            actions=[],
            extra=hxhy,
            object_name="deviceCardServo",
            parent=parent,
        )
        self._hxhy = hxhy
        self._servo_probe_label = card.findChild(QLabel, "deviceCardValue0")
        self._servo_hy_label = card.findChild(QLabel, "deviceCardValue1")
        self._servo_cal_label = card.findChild(QLabel, "deviceCardValue4")
        return card

    def _on_jog_action(self, action: str) -> None:
        motion = self._manager.motion
        mapping = {
            "X+": ("x", "+"),
            "X-": ("x", "-"),
            "Y+": ("y", "+"),
            "Y-": ("y", "-"),
            "Z+": ("z", "+"),
            "Z-": ("z", "-"),
        }
        if action in mapping:
            axis, direction = mapping[action]
            message = motion.jog(axis, direction)
            self._show_result(message)
            return
        if action == "●":
            message = "Mock：运动平台 Jog 中心（Mock 无移动）"
            self._show_result(message)

    def _on_servo_action(self, action: str) -> None:
        servo = self._manager.servo
        if action == "切换到 Hx":
            message = servo.switch_to_hx()
            self._hxhy.set_probe("Hx")
        elif action == "切换到 Hy":
            message = servo.switch_to_hy()
            self._hxhy.set_probe("Hy")
        elif action == "Hx/Hy 校准":
            message = servo.calibrate()
        elif action == "应用偏移补偿":
            message = servo.apply_offset()
        else:
            message = f"Mock：舵机操作 {action}"
        self._show_result(message)

    def _on_card_action(self, action: str) -> None:
        motion = self._manager.motion
        spectrum = self._manager.spectrum
        camera = self._manager.camera

        handlers = {
            "回零": motion.home,
            "停止": motion.stop,
            "刷新位置": motion.refresh_position,
            "测试连接": spectrum.test_connection,
            "单次 Sweep": spectrum.single_sweep,
            "读取 Trace": spectrum.read_trace,
            "拍照": camera.capture,
            "刷新预览": camera.refresh_preview,
            "打开相机设置": camera.open_settings,
        }
        handler = handlers.get(action)
        if handler is None:
            self._show_result(f"Mock：设备操作 {action}")
            return
        self._show_result(handler())

    def _show_result(self, message: str) -> None:
        if not message.startswith("Mock："):
            message = f"Mock：{message}"
        print(f"[Mock UI] {message}", flush=True)
        self.action_triggered.emit(message.removeprefix("Mock："))
        win = self.window()
        status = getattr(win, "_status", None)
        if status is not None:
            status.set_state(message)
        self._refresh_from_manager()

    def _refresh_from_manager(self) -> None:
        self._manager.sync_mock_data()
        m = self._manager.motion
        if self._motion_status_label is not None:
            self._motion_status_label.setText(m.status_text())
        if self._motion_position_label is not None:
            self._motion_position_label.setText(
                f"X {m.x:.2f} / Y {m.y:.2f} / Z {m.z:.2f} mm"
            )
        s = self._manager.servo
        if self._servo_probe_label is not None:
            self._servo_probe_label.setText(s.current_probe)
        if self._servo_hy_label is not None:
            self._servo_hy_label.setText(s.hy_status)
        if self._servo_cal_label is not None:
            self._servo_cal_label.setText(s.calibration)
        win = self.window()
        device_bar = getattr(win, "_device_bar", None)
        if device_bar is not None and hasattr(device_bar, "refresh_from_manager"):
            device_bar.refresh_from_manager()
