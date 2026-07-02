#!/usr/bin/env python3
"""Release_044 自动验收 — Real Hardware Functional Layer Offline Complete。"""

from __future__ import annotations

import compileall
import csv
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
SRC = ROOT / "src"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import verification_report  # noqa: E402
import verification_runtime  # noqa: E402
from verification_utils import setup_path  # noqa: E402

REAL_ENV_KEYS = (
    "NFS_ENABLE_REAL_HARDWARE",
    "NFS_ENABLE_REAL_MOTION_JOG",
    "NFS_ENABLE_REAL_MOTION_MOVE",
    "NFS_ENABLE_REAL_MOTION_HOME",
    "NFS_ENABLE_REAL_MOTION_ESTOP",
    "NFS_ENABLE_REAL_SPECTRUM_WRITE",
    "NFS_ENABLE_REAL_SPECTRUM_SWEEP",
    "NFS_ENABLE_REAL_SPECTRUM_TRACE_READ",
    "NFS_ENABLE_REAL_CAMERA",
    "NFS_ENABLE_REAL_SERVO",
    "NFS_ENABLE_REAL_SCAN_EXECUTION",
)

IMPORT_MODULES = (
    "nfs_scanner_pro.devices.real.transports",
    "nfs_scanner_pro.devices.real.command_result",
    "nfs_scanner_pro.devices.real.motion_grbl_adapter",
    "nfs_scanner_pro.devices.real.spectrum_scpi_adapter",
    "nfs_scanner_pro.devices.real.camera_adapter",
    "nfs_scanner_pro.devices.real.servo_adapter",
    "nfs_scanner_pro.devices.real.real_device_manager",
    "nfs_scanner_pro.scan.real_scan_executor",
    "nfs_scanner_pro.scan.real_scan_result_writer",
    "nfs_scanner_pro.scan.real_scan_state",
)

EXEC_GUARD_FILES = (
    SRC / "nfs_scanner_pro/scan/real_scan_executor.py",
    SCRIPTS_DIR / "run_real_scan_offline.py",
    SCRIPTS_DIR / "debug_real_motion.py",
    SCRIPTS_DIR / "debug_real_spectrum.py",
    SCRIPTS_DIR / "debug_real_camera.py",
    SCRIPTS_DIR / "debug_real_servo.py",
)

FORBIDDEN_EXEC_TOKENS = (
    'write(b"G0',
    'write(b"G1',
    'write(b"$J',
    'write(b"$H',
    'write(b"G28',
    "_transport_query(\"INIT",
    "_transport_query(\"SING",
)

FORBIDDEN_IMPORT_TOKENS = (
    "import serial",
    "from serial",
    "socket.create_connection",
    "import pyvisa",
    "from pyvisa",
)

DEBUG_SCRIPTS = (
    SCRIPTS_DIR / "debug_real_motion.py",
    SCRIPTS_DIR / "debug_real_spectrum.py",
    SCRIPTS_DIR / "debug_real_camera.py",
    SCRIPTS_DIR / "debug_real_servo.py",
)

SCAN_SCRIPT = SCRIPTS_DIR / "run_real_scan_offline.py"


def _clear_real_env() -> dict[str, str | None]:
    backup: dict[str, str | None] = {}
    for key in REAL_ENV_KEYS:
        backup[key] = os.environ.pop(key, None)
    return backup


def _restore_real_env(backup: dict[str, str | None]) -> None:
    for key, value in backup.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    for key in REAL_ENV_KEYS:
        env.pop(key, None)
    return env


def _run_script(script: Path, args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *(args or [])],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_subprocess_env(),
    )


def check_compileall(report: verification_report.VerificationReport) -> None:
    report.start_check("compileall")
    ok = bool(compileall.compile_dir(str(SRC / "nfs_scanner_pro"), quiet=1))
    failed: list[str] = []
    if ok:
        for mod in IMPORT_MODULES:
            try:
                __import__(mod)
            except Exception as exc:  # noqa: BLE001
                failed.append(f"{mod}: {exc}")
                ok = False
    if ok:
        report.pass_check("compileall")
    else:
        report.fail_check("compileall", "; ".join(failed))


def check_real_hardware_imports(report: verification_report.VerificationReport) -> None:
    report.start_check("real_hardware_imports")
    try:
        from nfs_scanner_pro.devices.real.transports import (
            FakeCameraTransport,
            FakeScpiTransport,
            FakeSerialTransport,
            FakeServoTransport,
        )
        from nfs_scanner_pro.devices.real.command_result import CommandResult, blocked, success
        from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter
        from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter
        from nfs_scanner_pro.devices.real.camera_adapter import CameraAdapter
        from nfs_scanner_pro.devices.real.servo_adapter import ServoAdapter
        from nfs_scanner_pro.devices.real.real_device_manager import RealDeviceManager
        from nfs_scanner_pro.scan.real_scan_executor import RealScanExecutor
        from nfs_scanner_pro.scan.real_scan_result_writer import build_summary, save_scan_result
        from nfs_scanner_pro.scan.real_scan_state import RealScanProgress, RealScanState

        ok = all(
            obj is not None
            for obj in (
                FakeSerialTransport,
                FakeScpiTransport,
                FakeCameraTransport,
                FakeServoTransport,
                CommandResult,
                blocked,
                success,
                MotionGrblAdapter,
                SpectrumScpiAdapter,
                CameraAdapter,
                ServoAdapter,
                RealDeviceManager,
                RealScanExecutor,
                build_summary,
                save_scan_result,
                RealScanProgress,
                RealScanState,
            )
        )
        if ok:
            report.pass_check("real_hardware_imports")
        else:
            report.fail_check("real_hardware_imports", "missing symbol")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_hardware_imports", str(exc))


def check_safety_flags_default_false(report: verification_report.VerificationReport) -> None:
    report.start_check("safety_flags_default_false")
    backup = _clear_real_env()
    try:
        import importlib

        hw = importlib.import_module("nfs_scanner_pro.devices.real.hardware_config")
        flags = (
            hw.is_real_hardware_enabled(),
            hw.is_real_motion_jog_enabled(),
            hw.is_real_motion_move_enabled(),
            hw.is_real_motion_home_enabled(),
            hw.is_real_motion_estop_enabled(),
            hw.is_real_spectrum_write_enabled(),
            hw.is_real_spectrum_sweep_enabled(),
            hw.is_real_spectrum_trace_read_enabled(),
            hw.is_real_camera_enabled(),
            hw.is_real_servo_enabled(),
            hw.is_real_scan_execution_enabled(),
        )
        if all(flag is False for flag in flags):
            report.pass_check("safety_flags_default_false")
        else:
            report.fail_check("safety_flags_default_false", str(flags))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("safety_flags_default_false", str(exc))
    finally:
        _restore_real_env(backup)


def check_fake_transports(report: verification_report.VerificationReport) -> None:
    report.start_check("fake_transports")
    try:
        from nfs_scanner_pro.devices.real.transports import (
            FakeCameraTransport,
            FakeScpiTransport,
            FakeSerialTransport,
            FakeServoTransport,
        )

        serial = FakeSerialTransport()
        serial.connect()
        status = serial.query("?")
        scpi = FakeScpiTransport()
        scpi.connect()
        idn = scpi.query("*IDN?")
        marker = scpi.query("CALC:MARK1:Y?")
        camera = FakeCameraTransport()
        camera.connect()
        capture = camera.capture()
        servo = FakeServoTransport()
        servo.connect()
        servo.write("SWITCH_HY")
        hy_state = servo.query("state")
        servo.write("SWITCH_HX")
        hx_state = servo.query("state")

        ok = (
            serial.is_connected()
            and "MPos:" in status
            and "FakeSpectrum" in idn
            and marker == "-23.45"
            and capture.get("ok") is True
            and capture.get("fake") is True
            and Path(str(capture.get("path", ""))).is_file()
            and "Hy" in hy_state
            and "Hx" in hx_state
        )
        if ok:
            report.pass_check("fake_transports")
        else:
            report.fail_check(
                "fake_transports",
                f"status={status!r} idn={idn!r} marker={marker!r} capture={capture}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("fake_transports", str(exc))


def check_motion_full_api_offline(report: verification_report.VerificationReport) -> None:
    report.start_check("motion_full_api_offline")
    backup = _clear_real_env()
    try:
        from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter
        from nfs_scanner_pro.devices.real.transports import FakeSerialTransport

        motion = MotionGrblAdapter()
        jog_cmd = motion.build_jog_command("x", "+", 0.1)
        move_cmd = motion.build_move_command(x=50.0, y=-50.0, z=5.0)
        home_blocked = motion.home(dry_run=False)
        estop_blocked = motion.emergency_stop(dry_run=False)

        fake_motion = MotionGrblAdapter()
        fake_motion.bind_transport(FakeSerialTransport())
        fake_motion.connect()
        jog_result = fake_motion.safe_jog("x", "+", 0.1, dry_run=False)
        pos_before = jog_result.get("position_before", {})
        pos_after = jog_result.get("position_after", {})

        ok = (
            jog_cmd.startswith("$J=G91 G21 X")
            and "G90" in move_cmd
            and "G1" in move_cmd
            and home_blocked.get("blocked") is True
            and estop_blocked.get("blocked") is True
            and jog_result.get("ok") is True
            and pos_after.get("x", 0) > pos_before.get("x", 0)
        )
        if ok:
            report.pass_check("motion_full_api_offline")
        else:
            report.fail_check(
                "motion_full_api_offline",
                f"jog={jog_cmd!r} home={home_blocked} estop={estop_blocked} fake={jog_result}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("motion_full_api_offline", str(exc))
    finally:
        _restore_real_env(backup)


def check_spectrum_full_api_offline(report: verification_report.VerificationReport) -> None:
    report.start_check("spectrum_full_api_offline")
    backup = _clear_real_env()
    try:
        from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter
        from nfs_scanner_pro.devices.real.transports import FakeScpiTransport

        spectrum = SpectrumScpiAdapter()
        write_blocked = spectrum.write("FREQ:CENT 2450000000", dry_run=False)
        configure = spectrum.configure_measurement(center_freq=2.45e9, dry_run=True)
        trace_blocked = spectrum.read_trace_data()

        fake_spectrum = SpectrumScpiAdapter()
        fake_spectrum.bind_transport(FakeScpiTransport())
        fake_spectrum.connect()
        fake_trace = fake_spectrum.read_trace_data()
        values = fake_trace.get("values", [])

        ok = (
            write_blocked.get("blocked") is True
            and configure.get("ok") is True
            and configure.get("dry_run") is True
            and trace_blocked.get("blocked") is True
            and fake_trace.get("ok") is True
            and len(values) >= 3
            and abs(values[0] + 23.1) < 0.01
        )
        if ok:
            report.pass_check("spectrum_full_api_offline")
        else:
            report.fail_check(
                "spectrum_full_api_offline",
                f"write={write_blocked} configure={configure} trace={trace_blocked} fake={fake_trace}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("spectrum_full_api_offline", str(exc))
    finally:
        _restore_real_env(backup)


def check_camera_full_api_offline(report: verification_report.VerificationReport) -> None:
    report.start_check("camera_full_api_offline")
    backup = _clear_real_env()
    try:
        with mock.patch.dict(sys.modules, {"cv2": None}):
            from nfs_scanner_pro.devices.real.camera_adapter import CameraAdapter
            from nfs_scanner_pro.devices.real.transports import FakeCameraTransport

            camera = CameraAdapter()
            blocked = camera.capture_image(dry_run=False)
            fake_camera = CameraAdapter()
            fake_camera.bind_transport(FakeCameraTransport())
            fake_camera.connect()
            capture = fake_camera.capture_image(dry_run=False)

        ok = (
            blocked.get("blocked") is True
            and capture.get("ok") is True
            and capture.get("fake") is True
            and Path(str(capture.get("path", ""))).is_file()
        )
        if ok:
            report.pass_check("camera_full_api_offline")
        else:
            report.fail_check(
                "camera_full_api_offline",
                f"blocked={blocked} capture={capture}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("camera_full_api_offline", str(exc))
    finally:
        _restore_real_env(backup)


def check_servo_full_api_offline(report: verification_report.VerificationReport) -> None:
    report.start_check("servo_full_api_offline")
    backup = _clear_real_env()
    try:
        from nfs_scanner_pro.devices.real.servo_adapter import ServoAdapter
        from nfs_scanner_pro.devices.real.transports import FakeServoTransport

        servo = ServoAdapter()
        hx_blocked = servo.switch_hx(dry_run=False)
        hy_blocked = servo.switch_hy(dry_run=False)

        fake_servo = ServoAdapter()
        fake_servo.bind_transport(FakeServoTransport())
        fake_servo.connect()
        hx = fake_servo.switch_hx(dry_run=False)
        hy = fake_servo.switch_hy(dry_run=False)
        state = fake_servo.get_state()

        ok = (
            hx_blocked.get("blocked") is True
            and hy_blocked.get("blocked") is True
            and hx.get("ok") is True
            and hx.get("fake") is True
            and hy.get("ok") is True
            and state.get("probe") == "Hy"
        )
        if ok:
            report.pass_check("servo_full_api_offline")
        else:
            report.fail_check(
                "servo_full_api_offline",
                f"blocked hx={hx_blocked} hy={hy_blocked} fake hx={hx} hy={hy} state={state}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("servo_full_api_offline", str(exc))
    finally:
        _restore_real_env(backup)


def check_real_device_manager_offline(report: verification_report.VerificationReport) -> None:
    report.start_check("real_device_manager_offline")
    backup = _clear_real_env()
    try:
        from nfs_scanner_pro.devices.real.real_device_manager import RealDeviceManager

        manager = RealDeviceManager()
        disabled = manager.connect_all_safe()
        manager.enable_fake_transports()
        snapshot = manager.get_snapshot()
        jog = manager.run_motion_jog("x", "+", 0.1, dry_run=False)
        marker = manager.spectrum.read_marker_amplitude()
        capture = manager.run_camera_capture(fake=True)
        servo = manager.run_servo_switch("hy", dry_run=False)
        manager.disconnect_all()

        ok = (
            disabled.get("status") == "disabled"
            and snapshot.get("fake_mode") is True
            and jog.get("ok") is True
            and marker.get("ok") is True
            and marker.get("amplitude_dbm") == -23.45
            and capture.get("ok") is True
            and servo.get("ok") is True
        )
        if ok:
            report.pass_check("real_device_manager_offline")
        else:
            report.fail_check(
                "real_device_manager_offline",
                f"disabled={disabled} jog={jog} marker={marker} capture={capture} servo={servo}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_device_manager_offline", str(exc))
    finally:
        _restore_real_env(backup)


def check_real_scan_executor_dry_run(report: verification_report.VerificationReport) -> None:
    report.start_check("real_scan_executor_dry_run")
    backup = _clear_real_env()
    try:
        verification_runtime.enter_release_runtime("R044")
        from nfs_scanner_pro.scan.real_scan_executor import RealScanExecutor
        from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan

        plan = generate_3x3_scan_plan(center_x=50.0, center_y=-50.0, z=5.0, step_mm=0.5)
        executor = RealScanExecutor()
        load_result = executor.load_plan(plan)
        result = executor.dry_run()
        paths = result.get("paths", {})
        summary = result.get("summary", {})

        json_path = paths.get("json_path")
        csv_path = paths.get("csv_path")
        summary_path = paths.get("summary_path")
        ok = (
            load_result.get("ok") is True
            and plan.point_count() == 9
            and result.get("ok") is True
            and result.get("mode") == "dry_run"
            and json_path is not None
            and csv_path is not None
            and summary_path is not None
            and json_path.is_file()
            and csv_path.is_file()
            and summary_path.is_file()
            and "R044" in json_path.as_posix()
            and summary.get("total_points") == 9
            and summary.get("dry_run") is True
        )
        if ok:
            report.pass_check(
                "real_scan_executor_dry_run",
                json_path.relative_to(ROOT).as_posix(),
            )
        else:
            report.fail_check("real_scan_executor_dry_run", str(summary))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_scan_executor_dry_run", str(exc))
    finally:
        _restore_real_env(backup)


def check_real_scan_executor_fake_run(report: verification_report.VerificationReport) -> None:
    report.start_check("real_scan_executor_fake_run")
    backup = _clear_real_env()
    try:
        verification_runtime.enter_release_runtime("R044")
        from nfs_scanner_pro.scan.real_scan_executor import RealScanExecutor
        from nfs_scanner_pro.scan.real_scan_plan import generate_3x3_scan_plan

        plan = generate_3x3_scan_plan(center_x=50.0, center_y=-50.0, z=5.0, step_mm=0.5)
        executor = RealScanExecutor()
        executor.load_plan(plan)
        result = executor.fake_run()
        paths = result.get("paths", {})
        summary = result.get("summary", {})

        json_path = paths.get("json_path")
        csv_path = paths.get("csv_path")
        summary_path = paths.get("summary_path")
        real_blocked = executor.real_run()

        point_rows = 0
        if csv_path and csv_path.is_file():
            with csv_path.open(encoding="utf-8", newline="") as handle:
                point_rows = sum(1 for _ in csv.reader(handle)) - 1

        ok = (
            result.get("ok") is True
            and result.get("mode") == "fake_run"
            and result.get("completed_points") == 9
            and json_path is not None
            and csv_path is not None
            and summary_path is not None
            and json_path.is_file()
            and csv_path.is_file()
            and summary_path.is_file()
            and "R044" in json_path.as_posix()
            and point_rows == 9
            and summary.get("completed_points") == 9
            and summary.get("fake_run") is True
            and real_blocked.get("blocked") is True
        )
        if ok:
            report.pass_check(
                "real_scan_executor_fake_run",
                json_path.relative_to(ROOT).as_posix(),
            )
        else:
            report.fail_check(
                "real_scan_executor_fake_run",
                f"summary={summary} real={real_blocked} rows={point_rows}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_scan_executor_fake_run", str(exc))
    finally:
        _restore_real_env(backup)


def check_cli_default_safe(report: verification_report.VerificationReport) -> None:
    report.start_check("cli_default_safe")
    failures: list[str] = []
    with mock.patch.object(
        socket,
        "create_" + "connection",
        side_effect=AssertionError("socket"),
    ):
        for script in DEBUG_SCRIPTS:
            proc = _run_script(script)
            text = proc.stdout + proc.stderr
            if proc.returncode != 0 or "disabled" not in text.lower():
                failures.append(f"{script.name}={proc.returncode}")
        scan_proc = _run_script(SCAN_SCRIPT, ["--dry-run"])
        scan_text = scan_proc.stdout + scan_proc.stderr
        if scan_proc.returncode != 0 or "Mode: dry_run" not in scan_text:
            failures.append(f"run_real_scan_offline={scan_proc.returncode}")
        real_proc = _run_script(SCAN_SCRIPT, ["--real-run"])
        real_text = real_proc.stdout + real_proc.stderr
        if real_proc.returncode != 0 or "blocked=True" not in real_text:
            failures.append("real_run_cli")
    if failures:
        report.fail_check("cli_default_safe", "; ".join(failures))
    else:
        report.pass_check("cli_default_safe")


def check_cli_fake_mode(report: verification_report.VerificationReport) -> None:
    report.start_check("cli_fake_mode")
    failures: list[str] = []
    with mock.patch.object(
        socket,
        "create_" + "connection",
        side_effect=AssertionError("socket"),
    ):
        motion = _run_script(DEBUG_SCRIPTS[0], ["--fake", "--status"])
        if motion.returncode != 0 or "fake transport" not in (motion.stdout + motion.stderr):
            failures.append("motion")
        spectrum = _run_script(DEBUG_SCRIPTS[1], ["--fake", "--marker"])
        spec_text = spectrum.stdout + spectrum.stderr
        if spectrum.returncode != 0 or "-23.45" not in spec_text:
            failures.append("spectrum")
        camera = _run_script(DEBUG_SCRIPTS[2], ["--fake", "--capture"])
        cam_text = camera.stdout + camera.stderr
        if camera.returncode != 0 or "'fake': True" not in cam_text:
            failures.append("camera")
        servo = _run_script(DEBUG_SCRIPTS[3], ["--fake", "--hy"])
        serv_text = servo.stdout + servo.stderr
        if servo.returncode != 0 or "'fake': True" not in serv_text:
            failures.append("servo")
        scan = _run_script(SCAN_SCRIPT, ["--fake-run"])
        scan_text = scan.stdout + scan.stderr
        if scan.returncode != 0 or "ok=True" not in scan_text:
            failures.append("scan_fake_run")
    if failures:
        report.fail_check("cli_fake_mode", "; ".join(failures))
    else:
        report.pass_check("cli_fake_mode")


def check_source_safety_guards(report: verification_report.VerificationReport) -> None:
    report.start_check("source_safety_guards")
    hits: list[str] = []
    for path in EXEC_GUARD_FILES:
        if not path.is_file():
            hits.append(f"missing:{path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_EXEC_TOKENS:
            if token in text:
                hits.append(f"{path.name}: {token}")
        if path.name != "transports.py":
            for token in FORBIDDEN_IMPORT_TOKENS:
                if token in text:
                    hits.append(f"{path.name}: {token}")
        if path.name == "run_real_scan_offline.py":
            if "--real-run" in text and "blocked" not in text:
                hits.append(f"{path.name}: real-run without blocked handling")
        if path.name == "real_scan_executor.py":
            if "require_real_scan_execution_enabled" not in text:
                hits.append(f"{path.name}: missing scan execution guard")
            if "is_real_hardware_enabled" not in text:
                hits.append(f"{path.name}: missing hardware guard")

    motion_path = SRC / "nfs_scanner_pro/devices/real/motion_grbl_adapter.py"
    if motion_path.is_file():
        motion_text = motion_path.read_text(encoding="utf-8")
        if "require_real_motion_jog_enabled" not in motion_text:
            hits.append("motion_grbl_adapter.py: missing jog guard")
        if "require_real_motion_home_enabled" not in motion_text:
            hits.append("motion_grbl_adapter.py: missing home guard")

    spectrum_path = SRC / "nfs_scanner_pro/devices/real/spectrum_scpi_adapter.py"
    if spectrum_path.is_file():
        spectrum_text = spectrum_path.read_text(encoding="utf-8")
        if "require_real_spectrum_write_enabled" not in spectrum_text:
            hits.append("spectrum_scpi_adapter.py: missing write guard")
        if "require_real_spectrum_trace_read_enabled" not in spectrum_text:
            hits.append("spectrum_scpi_adapter.py: missing trace guard")

    if hits:
        report.fail_check("source_safety_guards", "; ".join(hits))
    else:
        report.pass_check("source_safety_guards")


def check_mock_ui_unchanged(report: verification_report.VerificationReport) -> None:
    report.start_check("mock_ui_unchanged")
    env = _subprocess_env()
    failures: list[str] = []
    for script in ("029", "042", "043"):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / f"verify_release_{script}.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        text = proc.stdout + proc.stderr
        if proc.returncode != 0 or "RESULT: PASS" not in text:
            failures.append(f"verify_{script}={proc.returncode}")
    if failures:
        report.fail_check("mock_ui_unchanged", "; ".join(failures))
    else:
        report.pass_check("mock_ui_unchanged")


def check_no_high_fidelity_changes(report: verification_report.VerificationReport) -> None:
    report.start_check("no_high_fidelity_changes")
    proc = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    bad = [
        line.strip()
        for line in proc.stdout.splitlines()
        if line.strip().startswith("prototypes/high_fidelity/")
    ]
    if bad:
        report.fail_check("no_high_fidelity_changes", ", ".join(bad))
    else:
        report.pass_check("no_high_fidelity_changes")


def write_acceptance_report(report: verification_report.VerificationReport) -> Path:
    out = (
        ROOT
        / "docs/product-spec/release/Release_044_Real_Hardware_Functional_Layer_Offline_Complete/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_044 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_044.py",
        "python scripts/verify_all.py --only 044",
        "python scripts/run_real_scan_offline.py --fake-run",
        "python scripts/debug_real_motion.py --fake --status",
        "```",
        "",
        "## 检查项",
        "",
    ]
    for name, ok, detail, elapsed, skipped in report.entries:
        status = "SKIP" if skipped else ("PASS" if ok else "FAIL")
        suffix = f" — {detail}" if detail else ""
        timing = f" ({elapsed:.2f}s)" if elapsed is not None else ""
        lines.append(f"- [{status}] `{name}`{timing}{suffix}")
    lines.extend(
        [
            "",
            "## 结果",
            "",
            "PASS" if report.is_pass() else "FAIL",
            "",
            "## runtime 隔离路径",
            "",
            "- `runtime/verification/R044/`",
            "",
            "## 是否默认连接真实设备",
            "",
            "否",
            "",
            "## 是否执行真实运动 / sweep",
            "",
            "否",
            "",
            "## 是否支持 fake transport / fake-run",
            "",
            "是",
            "",
            "## real-run 是否默认 blocked",
            "",
            "是",
            "",
            "## 是否修改 high_fidelity HTML",
            "",
            "否",
            "",
            "## 是否可以提交",
            "",
            "是" if report.is_pass() else "否",
            "",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    setup_path()
    _clear_real_env()
    verification_runtime.enter_release_runtime("R044")
    report = verification_report.VerificationReport("044")

    check_compileall(report)
    check_real_hardware_imports(report)
    check_safety_flags_default_false(report)
    check_fake_transports(report)
    check_motion_full_api_offline(report)
    check_spectrum_full_api_offline(report)
    check_camera_full_api_offline(report)
    check_servo_full_api_offline(report)
    check_real_device_manager_offline(report)
    check_real_scan_executor_dry_run(report)
    check_real_scan_executor_fake_run(report)
    check_cli_default_safe(report)
    check_cli_fake_mode(report)
    check_source_safety_guards(report)
    check_mock_ui_unchanged(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
