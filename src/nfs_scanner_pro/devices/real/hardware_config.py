"""真实硬件配置 — Release 036 / 047 YAML + 环境变量。"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_CONFIG_SOURCES: dict[str, str] = {}
_YAML_LOAD_NOTE = ""
_YAML_DATA: dict[str, Any] | None = None


def _project_root() -> Path:
    from nfs_scanner_pro.app_paths import get_project_root

    return get_project_root()


def _local_yaml_path() -> Path:
    return _project_root() / "config" / "hardware.local.yaml"


def _yaml_load_note() -> str:
    _ensure_yaml_loaded()
    return _YAML_LOAD_NOTE


def _ensure_yaml_loaded() -> dict[str, Any]:
    global _YAML_DATA, _YAML_LOAD_NOTE
    if _YAML_DATA is not None:
        return _YAML_DATA
    path = _local_yaml_path()
    if not path.is_file():
        _YAML_DATA = {}
        _YAML_LOAD_NOTE = "yaml_missing"
        return _YAML_DATA
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        _YAML_DATA = {}
        _YAML_LOAD_NOTE = "pyyaml_not_installed"
        return _YAML_DATA
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        _YAML_DATA = loaded if isinstance(loaded, dict) else {}
        _YAML_LOAD_NOTE = "yaml_loaded"
    except Exception as exc:  # noqa: BLE001
        _YAML_DATA = {}
        _YAML_LOAD_NOTE = f"yaml_error:{exc}"
    return _YAML_DATA


def _yaml_section(name: str) -> dict[str, Any]:
    data = _ensure_yaml_loaded()
    section = data.get(name, {})
    return section if isinstance(section, dict) else {}


def _record_source(key: str, source: str) -> None:
    _CONFIG_SOURCES[key] = source


def _env_or_yaml(env_key: str, yaml_value: Any, default: Any, *, config_key: str) -> Any:
    if env_key in os.environ and os.environ[env_key].strip() != "":
        _record_source(config_key, "env")
        return os.environ[env_key].strip()
    if yaml_value is not None and yaml_value != "":
        _record_source(config_key, "yaml")
        return yaml_value
    _record_source(config_key, "default")
    return default


def is_real_hardware_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_HARDWARE", "").strip() == "1"


def is_real_motion_jog_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_MOTION_JOG", "").strip() == "1"


def is_real_motion_move_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_MOTION_MOVE", "").strip() == "1"


def is_real_motion_home_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_MOTION_HOME", "").strip() == "1"


def is_real_motion_estop_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_MOTION_ESTOP", "").strip() == "1"


def is_real_spectrum_write_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_SPECTRUM_WRITE", "").strip() == "1"


def is_real_spectrum_sweep_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_SPECTRUM_SWEEP", "").strip() == "1"


def is_real_spectrum_trace_read_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_SPECTRUM_TRACE_READ", "").strip() == "1"


def is_real_camera_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_CAMERA", "").strip() == "1"


def is_real_servo_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_SERVO", "").strip() == "1"


def is_real_scan_execution_enabled() -> bool:
    return os.environ.get("NFS_ENABLE_REAL_SCAN_EXECUTION", "").strip() == "1"


def get_all_safety_flags() -> dict[str, bool]:
    return {
        "NFS_ENABLE_REAL_HARDWARE": is_real_hardware_enabled(),
        "NFS_ENABLE_REAL_MOTION_JOG": is_real_motion_jog_enabled(),
        "NFS_ENABLE_REAL_MOTION_MOVE": is_real_motion_move_enabled(),
        "NFS_ENABLE_REAL_MOTION_HOME": is_real_motion_home_enabled(),
        "NFS_ENABLE_REAL_MOTION_ESTOP": is_real_motion_estop_enabled(),
        "NFS_ENABLE_REAL_SPECTRUM_WRITE": is_real_spectrum_write_enabled(),
        "NFS_ENABLE_REAL_SPECTRUM_SWEEP": is_real_spectrum_sweep_enabled(),
        "NFS_ENABLE_REAL_SPECTRUM_TRACE_READ": is_real_spectrum_trace_read_enabled(),
        "NFS_ENABLE_REAL_CAMERA": is_real_camera_enabled(),
        "NFS_ENABLE_REAL_SERVO": is_real_servo_enabled(),
        "NFS_ENABLE_REAL_SCAN_EXECUTION": is_real_scan_execution_enabled(),
    }


@dataclass
class MotionConfig:
    port: str = "COM6"
    baudrate: int = 115200
    timeout: float = 2.0
    enabled: bool = False
    type: str = "grbl"


@dataclass
class MotionSafetyConfig:
    x_min: float = 0.0
    x_max: float = 200.0
    y_min: float = -200.0
    y_max: float = 0.0
    z_min: float = 0.0
    z_max: float = 50.0
    max_jog_step_mm: float = 1.0
    default_jog_step_mm: float = 0.1
    jog_feed_mm_min: float = 100.0


@dataclass
class SpectrumConfig:
    backend: str = "socket"
    host: str = "192.168.1.100"
    port: int = 5025
    timeout: float = 3.0
    visa_address: str = "TCPIP0::192.168.1.100::inst0::INSTR"
    enabled: bool = False
    default_marker: int = 1
    max_trace_points: int = 201

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


@dataclass
class CameraConfig:
    backend: str = "opencv"
    device_index: int = 0
    enabled: bool = False
    output_dir: str = "runtime/camera"


@dataclass
class ServoConfig:
    port: str = ""
    baudrate: int = 115200
    timeout: float = 2.0
    current_probe: str = "Hx"
    enabled: bool = False
    type: str = "serial"
    hx_angle: float = 0.0
    hy_angle: float = 90.0


@dataclass
class ScanConfig:
    enabled: bool = False
    max_points: int = 9
    dwell_ms: int = 200
    require_manual_confirm: bool = True
    output_dir: str = "runtime/real_scan_runs"


@dataclass
class HardwareConfig:
    hardware_mode: str = "mock"
    motion: MotionConfig = field(default_factory=MotionConfig)
    motion_safety: MotionSafetyConfig = field(default_factory=MotionSafetyConfig)
    spectrum: SpectrumConfig = field(default_factory=SpectrumConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    servo: ServoConfig = field(default_factory=ServoConfig)
    scan: ScanConfig = field(default_factory=ScanConfig)


def build_adapter_snapshot_common(
    *,
    enabled: bool,
    connected: bool,
    fake: bool,
    config: dict[str, Any],
    last_error: str = "",
    last_command: str = "",
    last_response: str = "",
    dry_run: bool = True,
) -> dict[str, Any]:
    from datetime import datetime, timezone

    return {
        "enabled": enabled,
        "connected": connected,
        "fake": fake,
        "dry_run": dry_run,
        "safe_mode": True,
        "config": config,
        "last_error": last_error,
        "last_command": last_command,
        "last_response": last_response,
        "timestamp_iso": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def load_motion_safety_config() -> MotionSafetyConfig:
    motion_yaml = _yaml_section("motion")
    return MotionSafetyConfig(
        x_min=float(_env_or_yaml("NFS_MOTION_X_MIN", motion_yaml.get("x_min"), "0.0", config_key="motion.x_min")),
        x_max=float(_env_or_yaml("NFS_MOTION_X_MAX", motion_yaml.get("x_max"), "200.0", config_key="motion.x_max")),
        y_min=float(_env_or_yaml("NFS_MOTION_Y_MIN", motion_yaml.get("y_min"), "-200.0", config_key="motion.y_min")),
        y_max=float(_env_or_yaml("NFS_MOTION_Y_MAX", motion_yaml.get("y_max"), "0.0", config_key="motion.y_max")),
        z_min=float(_env_or_yaml("NFS_MOTION_Z_MIN", motion_yaml.get("z_min"), "0.0", config_key="motion.z_min")),
        z_max=float(_env_or_yaml("NFS_MOTION_Z_MAX", motion_yaml.get("z_max"), "50.0", config_key="motion.z_max")),
        max_jog_step_mm=float(
            _env_or_yaml("NFS_MOTION_MAX_JOG_STEP_MM", motion_yaml.get("max_jog_step_mm"), "1.0", config_key="motion.max_jog_step_mm")
        ),
        default_jog_step_mm=float(
            _env_or_yaml(
                "NFS_MOTION_DEFAULT_JOG_STEP_MM",
                motion_yaml.get("default_jog_step_mm"),
                "0.1",
                config_key="motion.default_jog_step_mm",
            )
        ),
        jog_feed_mm_min=float(
            _env_or_yaml("NFS_MOTION_JOG_FEED_MM_MIN", motion_yaml.get("feed_mm_min"), "100", config_key="motion.feed_mm_min")
        ),
    )


def load_hardware_config() -> HardwareConfig:
    global _CONFIG_SOURCES
    _CONFIG_SOURCES = {}
    yaml_root = _ensure_yaml_loaded()
    motion_yaml = _yaml_section("motion")
    spectrum_yaml = _yaml_section("spectrum")
    camera_yaml = _yaml_section("camera")
    servo_yaml = _yaml_section("servo")
    scan_yaml = _yaml_section("scan")

    hardware_mode = str(
        _env_or_yaml("NFS_HARDWARE_MODE", yaml_root.get("hardware_mode"), "mock", config_key="hardware_mode")
    ).lower()

    motion = MotionConfig(
        port=str(_env_or_yaml("NFS_MOTION_PORT", motion_yaml.get("port"), "COM6", config_key="motion.port")),
        baudrate=int(_env_or_yaml("NFS_MOTION_BAUDRATE", motion_yaml.get("baudrate"), "115200", config_key="motion.baudrate")),
        timeout=float(_env_or_yaml("NFS_MOTION_TIMEOUT", motion_yaml.get("timeout"), "2.0", config_key="motion.timeout")),
        enabled=bool(motion_yaml.get("enabled", False)),
        type=str(motion_yaml.get("type", "grbl")),
    )
    motion_safety = load_motion_safety_config()

    host = str(_env_or_yaml("NFS_SPECTRUM_HOST", spectrum_yaml.get("host"), "192.168.1.100", config_key="spectrum.host"))
    port = int(_env_or_yaml("NFS_SPECTRUM_PORT", spectrum_yaml.get("port"), "5025", config_key="spectrum.port"))
    legacy_address = os.environ.get("NFS_SPECTRUM_ADDRESS", "")
    if legacy_address and ":" in legacy_address and "NFS_SPECTRUM_HOST" not in os.environ:
        host, _, port_text = legacy_address.rpartition(":")
        port = int(port_text)
        _record_source("spectrum.host", "env_legacy")
    visa_default = f"TCPIP0::{host}::inst0::INSTR"
    spectrum = SpectrumConfig(
        backend=str(
            _env_or_yaml("NFS_SPECTRUM_BACKEND", spectrum_yaml.get("backend"), "socket", config_key="spectrum.backend")
        ).lower(),
        host=host,
        port=port,
        visa_address=str(
            _env_or_yaml("NFS_SPECTRUM_VISA_ADDRESS", spectrum_yaml.get("visa_address"), visa_default, config_key="spectrum.visa_address")
        ),
        timeout=float(_env_or_yaml("NFS_SPECTRUM_TIMEOUT", spectrum_yaml.get("timeout"), "3.0", config_key="spectrum.timeout")),
        enabled=bool(spectrum_yaml.get("enabled", False)),
        default_marker=int(spectrum_yaml.get("default_marker", 1)),
        max_trace_points=int(spectrum_yaml.get("max_trace_points", 201)),
    )
    camera = CameraConfig(
        backend=str(_env_or_yaml("NFS_CAMERA_BACKEND", camera_yaml.get("backend"), "opencv", config_key="camera.backend")),
        device_index=int(_env_or_yaml("NFS_CAMERA_INDEX", camera_yaml.get("index"), "0", config_key="camera.index")),
        enabled=bool(camera_yaml.get("enabled", False)),
        output_dir=str(camera_yaml.get("output_dir", "runtime/camera")),
    )
    servo = ServoConfig(
        port=str(_env_or_yaml("NFS_SERVO_PORT", servo_yaml.get("port"), "", config_key="servo.port")),
        baudrate=int(_env_or_yaml("NFS_SERVO_BAUDRATE", servo_yaml.get("baudrate"), "115200", config_key="servo.baudrate")),
        timeout=float(_env_or_yaml("NFS_SERVO_TIMEOUT", servo_yaml.get("timeout"), "2.0", config_key="servo.timeout")),
        current_probe=str(_env_or_yaml("NFS_SERVO_PROBE", None, "Hx", config_key="servo.probe")),
        enabled=bool(servo_yaml.get("enabled", False)),
        type=str(servo_yaml.get("type", "serial")),
        hx_angle=float(servo_yaml.get("hx_angle", 0.0)),
        hy_angle=float(servo_yaml.get("hy_angle", 90.0)),
    )
    scan = ScanConfig(
        enabled=bool(scan_yaml.get("enabled", False)),
        max_points=int(scan_yaml.get("max_points", 9)),
        dwell_ms=int(scan_yaml.get("dwell_ms", 200)),
        require_manual_confirm=bool(scan_yaml.get("require_manual_confirm", True)),
        output_dir=str(scan_yaml.get("output_dir", "runtime/real_scan_runs")),
    )
    return HardwareConfig(
        hardware_mode=hardware_mode,
        motion=motion,
        motion_safety=motion_safety,
        spectrum=spectrum,
        camera=camera,
        servo=servo,
        scan=scan,
    )


def get_motion_config() -> dict[str, Any]:
    cfg = load_hardware_config()
    data = asdict(cfg.motion)
    data["safety"] = asdict(cfg.motion_safety)
    return data


def get_spectrum_config() -> dict[str, Any]:
    cfg = load_hardware_config()
    data = asdict(cfg.spectrum)
    data["address"] = cfg.spectrum.address
    return data


def get_camera_config() -> dict[str, Any]:
    return asdict(load_hardware_config().camera)


def get_servo_config() -> dict[str, Any]:
    return asdict(load_hardware_config().servo)


def get_scan_config() -> dict[str, Any]:
    return asdict(load_hardware_config().scan)


def get_config_source_summary() -> dict[str, Any]:
    load_hardware_config()
    return {
        "yaml_path": str(_local_yaml_path()),
        "yaml_status": _yaml_load_note(),
        "yaml_exists": _local_yaml_path().is_file(),
        "sources": dict(_CONFIG_SOURCES),
        "hardware_mode": _CONFIG_SOURCES.get("hardware_mode", "default"),
    }


def config_summary_as_json() -> str:
    return json.dumps(
        {
            "motion": get_motion_config(),
            "spectrum": get_spectrum_config(),
            "camera": get_camera_config(),
            "servo": get_servo_config(),
            "scan": get_scan_config(),
            "config_source": get_config_source_summary(),
            "safety_flags": get_all_safety_flags(),
        },
        ensure_ascii=False,
        indent=2,
    )


DISABLED_MESSAGE = (
    "真实设备未启用，请设置 NFS_ENABLE_REAL_HARDWARE=1 后再进行安全探测。"
)

SPECTRUM_DISABLED_MESSAGE = (
    "真实频谱仪未启用，请设置 NFS_ENABLE_REAL_HARDWARE=1"
)

JOG_DISABLED_MESSAGE = (
    "真实点动未启用，请设置 NFS_ENABLE_REAL_MOTION_JOG=1 后再进行手动点动。"
)

MOVE_DISABLED_MESSAGE = (
    "真实 move_to 未启用，请设置 NFS_ENABLE_REAL_MOTION_MOVE=1。"
)

HOME_DISABLED_MESSAGE = (
    "真实 home 未启用，请设置 NFS_ENABLE_REAL_MOTION_HOME=1。"
)

ESTOP_DISABLED_MESSAGE = (
    "真实急停未启用，请设置 NFS_ENABLE_REAL_MOTION_ESTOP=1。"
)

SPECTRUM_WRITE_DISABLED_MESSAGE = (
    "频谱仪写命令未启用，请设置 NFS_ENABLE_REAL_SPECTRUM_WRITE=1。"
)

SPECTRUM_SWEEP_DISABLED_MESSAGE = (
    "频谱 sweep 未启用，请设置 NFS_ENABLE_REAL_SPECTRUM_SWEEP=1。"
)

SPECTRUM_TRACE_DISABLED_MESSAGE = (
    "Trace 读取未启用，请设置 NFS_ENABLE_REAL_SPECTRUM_TRACE_READ=1。"
)

CAMERA_DISABLED_MESSAGE = (
    "真实相机未启用，请设置 NFS_ENABLE_REAL_CAMERA=1。"
)

SERVO_DISABLED_MESSAGE = (
    "真实舵机未启用，请设置 NFS_ENABLE_REAL_SERVO=1。"
)

SCAN_EXECUTION_DISABLED_MESSAGE = (
    "真实扫描执行未启用，请设置 NFS_ENABLE_REAL_SCAN_EXECUTION=1。"
)
