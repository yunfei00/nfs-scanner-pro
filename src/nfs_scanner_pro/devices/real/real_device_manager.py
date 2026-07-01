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
        self.camera = CameraAdapter(self.config.camera)
        self.servo = ServoAdapter(self.config.servo)
        self._devices = {
            DeviceType.MOTION: self.motion,
            DeviceType.SPECTRUM: self.spectrum,
            DeviceType.CAMERA: self.camera,
            DeviceType.SERVO: self.servo,
        }

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
        if self.spectrum.is_connected():
            spectrum_test = self.spectrum.test_connection()
            if isinstance(spectrum_test, dict):
                idn = spectrum_test.get("idn", {})
                freq = spectrum_test.get("frequency", {})
                trace = spectrum_test.get("trace_info", {})
                syst = spectrum_test.get("system_error", {})
                results["spectrum_test"] = "PASS" if spectrum_test.get("ok") else "FAIL"
                if isinstance(idn, dict):
                    results["spectrum_idn"] = str(idn.get("idn", idn.get("error", "")))
                if isinstance(syst, dict):
                    results["spectrum_syst_err"] = str(
                        syst.get("error_text", syst.get("error", ""))
                    )
                if isinstance(freq, dict) and freq.get("ok"):
                    results["spectrum_freq"] = (
                        f"{freq.get('frequency_ghz', 0):.6g} GHz"
                    )
                elif isinstance(freq, dict):
                    results["spectrum_freq"] = str(freq.get("error", ""))
                if isinstance(trace, dict) and trace.get("ok"):
                    results["spectrum_trace"] = ", ".join(trace.get("traces", []))
                elif isinstance(trace, dict):
                    results["spectrum_trace"] = str(trace.get("error", ""))
        elif self.enabled:
            spectrum_test = self.spectrum.test_connection()
            if isinstance(spectrum_test, dict):
                results["spectrum_test"] = str(
                    spectrum_test.get("error", spectrum_test.get("connect", "FAIL"))
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
        return build_device_snapshot(
            self.motion.snapshot(),
            self.spectrum.snapshot(),
            self.camera.snapshot(),
            self.servo.snapshot(),
        )

    def is_all_ready(self) -> bool:
        if not self.enabled:
            return False
        return all(device.is_connected() for device in self._devices.values())
