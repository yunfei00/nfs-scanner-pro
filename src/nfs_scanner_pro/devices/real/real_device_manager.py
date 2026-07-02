"""真实设备管理器 — 仅安全连接与查询（Release 036）。"""

from __future__ import annotations

from typing import Any

from nfs_scanner_pro.devices.device_snapshot import build_device_snapshot
from nfs_scanner_pro.devices.device_types import DeviceType, device_type_label
from nfs_scanner_pro.devices.real.camera_adapter import CameraAdapter
from nfs_scanner_pro.devices.real.hardware_config import (
    DISABLED_MESSAGE,
    HardwareConfig,
    is_real_hardware_enabled,
    load_hardware_config,
)
from nfs_scanner_pro.devices.real.joint_sample_adapter import JointSampleAdapter
from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter
from nfs_scanner_pro.devices.real.servo_adapter import ServoAdapter
from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter

_manager: RealDeviceManager | None = None


def get_real_device_manager() -> RealDeviceManager:
    global _manager
    if _manager is None:
        _manager = RealDeviceManager()
    return _manager


class RealDeviceManager:
    def __init__(self, config: HardwareConfig | None = None) -> None:
        self.config = config or load_hardware_config()
        self.motion = MotionGrblAdapter(self.config.motion, self.config.motion_safety)
        self.spectrum = SpectrumScpiAdapter(self.config.spectrum)
        self.joint_sample = JointSampleAdapter(self.motion, self.spectrum)
        self.camera = CameraAdapter(self.config.camera)
        self.servo = ServoAdapter(self.config.servo)
        self._devices = {
            DeviceType.MOTION: self.motion,
            DeviceType.SPECTRUM: self.spectrum,
            DeviceType.CAMERA: self.camera,
            DeviceType.SERVO: self.servo,
        }
        self._fake_mode = False

    def enable_fake_transports(self) -> None:
        from nfs_scanner_pro.devices.real.transports import (
            FakeCameraTransport,
            FakeScpiTransport,
            FakeSerialTransport,
            FakeServoTransport,
        )

        self._fake_mode = True
        self.motion.bind_transport(FakeSerialTransport())
        self.spectrum.bind_transport(FakeScpiTransport())
        self.camera.bind_transport(FakeCameraTransport())
        self.servo.bind_transport(FakeServoTransport())

    def run_motion_jog(
        self,
        axis: str,
        direction: str,
        step_mm: float,
        *,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        return self.motion.safe_jog(axis, direction, step_mm, dry_run=dry_run)

    def run_motion_move(
        self,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
        *,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        return self.motion.move_to(x, y, z, dry_run=dry_run)

    def run_motion_home(self, *, dry_run: bool = True) -> dict[str, Any]:
        return self.motion.home(dry_run=dry_run)

    def run_spectrum_configure(self, **kwargs: Any) -> dict[str, Any]:
        return self.spectrum.configure_measurement(dry_run=kwargs.pop("dry_run", True), **kwargs)

    def run_spectrum_sweep(self, *, dry_run: bool = True) -> dict[str, Any]:
        return self.spectrum.trigger_single_sweep(dry_run=dry_run)

    def run_camera_capture(self, *, dry_run: bool = True, fake: bool = False) -> dict[str, Any]:
        if fake and not self._fake_mode:
            self.enable_fake_transports()
        return self.camera.capture_image(dry_run=dry_run and not fake)

    def run_servo_switch(self, probe: str, *, dry_run: bool = True) -> dict[str, Any]:
        if probe.lower() == "hx":
            return self.servo.switch_hx(dry_run=dry_run)
        return self.servo.switch_hy(dry_run=dry_run)

    def run_joint_sample(self, *, save: bool = False) -> dict[str, Any]:
        return self.sample_single_point_safe(save=save)

    def run_scan_offline_or_real(
        self,
        executor: Any,
        mode: str = "dry_run",
    ) -> dict[str, Any]:
        if mode == "dry_run":
            return executor.dry_run()
        if mode == "fake_run":
            return executor.fake_run()
        return executor.real_run()

    @property
    def enabled(self) -> bool:
        return is_real_hardware_enabled()

    @property
    def disabled_reason(self) -> str:
        if self.enabled:
            return ""
        return DISABLED_MESSAGE

    def motion_safe_jog(
        self,
        axis: str,
        direction: str,
        step_mm: float,
        *,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        return self.motion.safe_jog(axis, direction, step_mm, dry_run=dry_run)

    def sample_single_point_safe(self, *, save: bool = True) -> dict[str, Any]:
        if not self.enabled:
            return {
                "ok": False,
                "disabled": True,
                "error": DISABLED_MESSAGE,
                "motion_command_executed": False,
                "sweep_started": False,
            }
        return self.joint_sample.sample_once_safe(save=save)

    def manual_sample_plan_point_safe(
        self,
        plan_point: dict[str, Any],
        tolerance_mm: float,
        *,
        save: bool = False,
    ) -> dict[str, Any]:
        """逐点手动采样：只读当前位置与频谱单点，校验容差，不运动。"""
        from nfs_scanner_pro.scan.manual_scan_session import (
            validate_position_near_plan_point,
        )

        if not self.enabled:
            return {
                "ok": False,
                "disabled": True,
                "error": DISABLED_MESSAGE,
                "motion_command_executed": False,
                "sweep_started": False,
            }

        motion_connected = False
        spectrum_connected = False
        outcome: dict[str, Any] = {
            "ok": False,
            "enabled": True,
            "motion_command_executed": False,
            "sweep_started": False,
        }
        try:
            motion_connect = self.motion.connect()
            outcome["motion_connect"] = motion_connect
            if not self.motion.is_connected():
                outcome["error"] = f"运动平台连接失败：{motion_connect}"
                return outcome
            motion_connected = True

            position = self.motion.refresh_position()
            outcome["motion_position"] = position
            if not isinstance(position, dict) or not position.get("ok"):
                outcome["error"] = str(
                    position.get("error", "运动平台位置读取失败")
                    if isinstance(position, dict)
                    else "运动平台位置读取失败"
                )
                return outcome

            planned = {
                "x": plan_point.get("x", plan_point.get("planned_x")),
                "y": plan_point.get("y", plan_point.get("planned_y")),
                "z": plan_point.get("z", plan_point.get("planned_z")),
            }
            validation = validate_position_near_plan_point(
                planned,
                {"x": position["x"], "y": position["y"], "z": position["z"]},
                tolerance_mm,
            )
            outcome["position_validation"] = validation
            if not validation.get("ok"):
                outcome["error"] = validation.get("reason", "位置超出容差")
                return outcome

            spectrum_connect = self.spectrum.connect()
            outcome["spectrum_connect"] = spectrum_connect
            if not self.spectrum.is_connected():
                outcome["error"] = f"频谱仪连接失败：{spectrum_connect}"
                return outcome
            spectrum_connected = True

            marker = self.spectrum.read_marker_amplitude()
            outcome["spectrum_marker"] = marker
            if not isinstance(marker, dict) or not marker.get("ok"):
                outcome["error"] = str(
                    marker.get("error", "频谱仪单点幅度读取失败")
                    if isinstance(marker, dict)
                    else "频谱仪单点幅度读取失败"
                )
                return outcome

            record = self.joint_sample.build_sample_record(position, marker)
            record["task_id"] = "MANUAL-3X3-POINT"
            outcome["record"] = record
            outcome["ok"] = True

            if save:
                json_path = self.joint_sample.save_sample_json(record)
                csv_path = self.joint_sample.save_sample_csv(record)
                outcome["json_path"] = str(json_path)
                outcome["csv_path"] = str(csv_path)
                record["sample_path"] = str(json_path)
            return outcome
        except Exception as exc:  # noqa: BLE001
            outcome["error"] = str(exc)
            return outcome
        finally:
            if spectrum_connected and self.spectrum.is_connected():
                try:
                    outcome["spectrum_disconnect"] = self.spectrum.disconnect()
                except Exception:  # noqa: BLE001
                    pass
            if motion_connected and self.motion.is_connected():
                try:
                    outcome["motion_disconnect"] = self.motion.disconnect()
                except Exception:  # noqa: BLE001
                    pass

    def connect_all_safe(self) -> dict[str, str]:
        if not self.enabled:
            return {"status": "disabled", "message": DISABLED_MESSAGE}
        return {
            "motion": self.motion.connect(),
            "spectrum": self.spectrum.connect(),
            "camera": self.camera.connect(),
            "servo": self.servo.connect(),
        }

    def disconnect_all(self) -> dict[str, str]:
        return {
            "motion": self.motion.disconnect(),
            "spectrum": self.spectrum.disconnect(),
            "camera": self.camera.disconnect(),
            "servo": self.servo.disconnect(),
        }

    def test_all_safe(self) -> dict[str, str]:
        if not self.enabled:
            return {"status": "disabled", "message": DISABLED_MESSAGE}
        results = self.connect_all_safe()
        if self.enabled:
            single = self.spectrum.read_single_point_amplitude()
            if isinstance(single, dict):
                marker = single.get("marker", single)
                results["spectrum_single_point"] = (
                    "PASS" if single.get("ok") else "FAIL"
                )
                if single.get("ok"):
                    results["spectrum_amplitude_dbm"] = str(
                        single.get("amplitude_dbm", marker.get("amplitude_dbm", ""))
                    )
                    results["spectrum_marker_raw"] = str(single.get("raw", ""))
                else:
                    results["spectrum_amplitude_dbm"] = str(
                        single.get("error", marker.get("error", ""))
                    )
        if self.motion.is_connected():
            status = self.motion.query_status()
            position = self.motion.refresh_position()
            if isinstance(status, dict):
                results["motion_status_raw"] = str(status.get("raw", ""))
                results["motion_state"] = str(status.get("state", ""))
            if isinstance(position, dict):
                results["motion_position"] = (
                    f"X={position.get('x', 0):.3f} "
                    f"Y={position.get('y', 0):.3f} "
                    f"Z={position.get('z', 0):.3f} "
                    f"({position.get('source', '')})"
                )
        if self.camera.is_connected():
            results["camera_devices"] = ", ".join(self.camera.enumerate_devices()) or "—"
        return results

    def get_device_status(self) -> list[dict[str, str]]:
        details = {
            DeviceType.MOTION: self.motion.port,
            DeviceType.SPECTRUM: self.spectrum.address,
            DeviceType.CAMERA: self.camera.interface,
            DeviceType.SERVO: self.servo.current_probe,
        }
        rows: list[dict[str, str]] = []
        for device_type, device in self._devices.items():
            if not self.enabled:
                status = "disabled"
            elif device_type is DeviceType.SPECTRUM and hasattr(device, "model"):
                if not self.enabled:
                    status = "disabled"
                elif device.is_connected():
                    status = device.model or device.state.value
                else:
                    status = device.state.value
            elif device_type is DeviceType.MOTION and hasattr(device, "grbl_state"):
                if device.is_connected():
                    grbl = getattr(device, "grbl_state", "") or device.state.value
                    status = grbl
                else:
                    status = device.state.value
            else:
                status = device.state.value if hasattr(device, "state") else "unknown"
            rows.append(
                {
                    "name": device_type_label(device_type),
                    "detail": details[device_type],
                    "status": status,
                }
            )
        return rows

    def get_snapshot(self) -> dict[str, Any]:
        snapshot = build_device_snapshot(
            self.motion.snapshot(),
            self.spectrum.snapshot(),
            self.camera.snapshot(),
            self.servo.snapshot(),
        )
        snapshot["joint_sample"] = self.joint_sample.snapshot()
        snapshot["fake_mode"] = self._fake_mode
        snapshot["hardware_flags"] = {
            "real_hardware": is_real_hardware_enabled(),
            "motion_jog": self.motion.snapshot().get("jog_enabled"),
            "motion_move": self.motion.snapshot().get("move_enabled"),
            "spectrum_write": self.spectrum.snapshot().get("write_enabled"),
            "camera": self.camera.snapshot().get("camera_enabled"),
            "servo": self.servo.snapshot().get("servo_enabled"),
        }
        return snapshot

    def is_all_ready(self) -> bool:
        if not self.enabled:
            return False
        return all(device.is_connected() for device in self._devices.values())
