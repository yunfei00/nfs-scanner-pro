#!/usr/bin/env python3
"""Release_041 自动验收 — Real Joint Single Point Sample。"""

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

IMPORT_MODULES = (
    "nfs_scanner_pro.devices.real.hardware_config",
    "nfs_scanner_pro.devices.real.hardware_safety",
    "nfs_scanner_pro.devices.real.real_device_manager",
    "nfs_scanner_pro.devices.real.motion_grbl_adapter",
    "nfs_scanner_pro.devices.real.spectrum_scpi_adapter",
    "nfs_scanner_pro.devices.real.joint_sample_adapter",
)

JOINT_ADAPTER_PATH = SRC / "nfs_scanner_pro/devices/real/joint_sample_adapter.py"
REAL_MANAGER_PATH = SRC / "nfs_scanner_pro/devices/real/real_device_manager.py"
CHECK_SCRIPT_PATH = SCRIPTS_DIR / "check_joint_single_point_sample_safe.py"

FORBIDDEN_EXEC_TOKENS = (
    'write(b"G0',
    'write(b"G1',
    'write(b"$J',
    'write(b"$H',
    'write(b"G28',
    "_transport_query(\"INIT",
    "_transport_query(\"SING",
    "CALC:DATA?",
    "TRAC:DATA?",
)


class FakeMotionAdapter:
    def __init__(self) -> None:
        self._connected = False
        self.connect_calls = 0
        self.disconnect_calls = 0

    def connect(self) -> str:
        self.connect_calls += 1
        self._connected = True
        return "motion connected"

    def disconnect(self) -> str:
        self.disconnect_calls += 1
        self._connected = False
        return "motion disconnected"

    def is_connected(self) -> bool:
        return self._connected

    def refresh_position(self) -> dict:
        return {
            "ok": True,
            "x": 45.2,
            "y": -28.3,
            "z": 5.0,
            "source": "MPos",
            "state": "Idle",
        }


class FakeSpectrumAdapter:
    def __init__(self) -> None:
        self._connected = False
        self.connect_calls = 0
        self.disconnect_calls = 0

    def connect(self) -> str:
        self.connect_calls += 1
        self._connected = True
        return "spectrum connected"

    def disconnect(self) -> str:
        self.disconnect_calls += 1
        self._connected = False
        return "spectrum disconnected"

    def is_connected(self) -> bool:
        return self._connected

    def read_marker_amplitude(self) -> dict:
        return {
            "ok": True,
            "source": "marker",
            "command": "CALC:MARK1:Y?",
            "frequency_hz": 2450000000.0,
            "frequency_ghz": 2.45,
            "amplitude": -23.45,
            "amplitude_dbm": -23.45,
            "unit": "dBm",
            "raw": "-23.45",
        }


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


def check_joint_sample_imports(report: verification_report.VerificationReport) -> None:
    report.start_check("joint_sample_imports")
    try:
        from nfs_scanner_pro.devices.real import (
            JointSampleAdapter,
            RealDeviceManager,
        )

        ok = JointSampleAdapter is not None and RealDeviceManager is not None
        if ok:
            report.pass_check("joint_sample_imports")
        else:
            report.fail_check("joint_sample_imports", "missing symbol")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("joint_sample_imports", str(exc))


def check_default_real_hardware_disabled(report: verification_report.VerificationReport) -> None:
    report.start_check("default_real_hardware_disabled")
    env_backup = os.environ.pop("NFS_ENABLE_REAL_HARDWARE", None)
    try:
        from nfs_scanner_pro.devices.real import JointSampleAdapter, RealDeviceManager
        from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter
        from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter

        adapter = JointSampleAdapter(MotionGrblAdapter(), SpectrumScpiAdapter())
        result = adapter.sample_once_safe(save=False)
        manager = RealDeviceManager()
        manager_result = manager.sample_single_point_safe(save=False)
        ok = (
            result.get("disabled") is True
            and manager_result.get("disabled") is True
            and result.get("motion_command_executed") is False
            and result.get("sweep_started") is False
        )
        if ok:
            report.pass_check("default_real_hardware_disabled")
        else:
            report.fail_check(
                "default_real_hardware_disabled",
                f"joint={result} manager={manager_result}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("default_real_hardware_disabled", str(exc))
    finally:
        if env_backup is not None:
            os.environ["NFS_ENABLE_REAL_HARDWARE"] = env_backup


def check_sample_record_builder(report: verification_report.VerificationReport) -> None:
    report.start_check("sample_record_builder")
    try:
        from nfs_scanner_pro.devices.real.joint_sample_adapter import JointSampleAdapter

        joint = JointSampleAdapter(None, None)
        motion = {
            "x": 45.2,
            "y": -28.3,
            "z": 5.0,
            "source": "MPos",
            "state": "Idle",
        }
        spectrum = {
            "frequency_hz": 2450000000.0,
            "frequency_ghz": 2.45,
            "amplitude_dbm": -23.45,
            "unit": "dBm",
            "source": "marker",
            "raw": "-23.45",
        }
        record = joint.build_sample_record(motion, spectrum)
        ok = (
            record.get("sample_id", "").startswith("SP-")
            and record.get("timestamp_iso")
            and record["position"]["x"] == 45.2
            and record["spectrum"]["frequency_hz"] == 2450000000.0
            and record["spectrum"]["amplitude_dbm"] == -23.45
            and record.get("safe_mode") is True
            and record.get("real_hardware") is True
            and record.get("motion_command_executed") is False
            and record.get("sweep_started") is False
        )
        if ok:
            report.pass_check("sample_record_builder")
        else:
            report.fail_check("sample_record_builder", str(record))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("sample_record_builder", str(exc))


def check_sample_json_csv_persistence(report: verification_report.VerificationReport) -> None:
    report.start_check("sample_json_csv_persistence")
    try:
        verification_runtime.enter_release_runtime("R041")
        from nfs_scanner_pro.devices.real.joint_sample_adapter import JointSampleAdapter

        joint = JointSampleAdapter(None, None)
        record = joint.build_sample_record(
            {"x": 1.0, "y": 2.0, "z": 3.0, "source": "MPos", "state": "Idle"},
            {
                "frequency_hz": 1e9,
                "frequency_ghz": 1.0,
                "amplitude_dbm": -10.0,
                "unit": "dBm",
                "source": "marker",
                "raw": "-10.0",
            },
        )
        json_path = joint.save_sample_json(record)
        csv_path = joint.save_sample_csv(record)
        runtime_root = verification_runtime.get_release_runtime_dir("041")
        joint_root = runtime_root / "joint_samples"
        ok = (
            json_path.is_file()
            and csv_path.is_file()
            and json.loads(json_path.read_text(encoding="utf-8"))["sample_id"] == record["sample_id"]
            and "R041" in json_path.as_posix()
            and "joint_samples" in json_path.as_posix()
            and joint_root.is_dir()
        )
        if ok:
            with csv_path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))
            ok = len(rows) == 2 and len(rows[0]) == len(rows[1])
        if ok:
            report.pass_check("sample_json_csv_persistence", json_path.relative_to(ROOT).as_posix())
        else:
            report.fail_check("sample_json_csv_persistence", f"json={json_path} csv={csv_path}")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("sample_json_csv_persistence", str(exc))


def check_no_connection_when_disabled(report: verification_report.VerificationReport) -> None:
    report.start_check("no_connection_when_disabled")
    env_backup = os.environ.pop("NFS_ENABLE_REAL_HARDWARE", None)
    try:
        from nfs_scanner_pro.devices.real.joint_sample_adapter import JointSampleAdapter
        from nfs_scanner_pro.devices.real.motion_grbl_adapter import MotionGrblAdapter
        from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter

        motion = MotionGrblAdapter()
        spectrum = SpectrumScpiAdapter()
        joint = JointSampleAdapter(motion, spectrum)
        with mock.patch.object(
            socket,
            "create_" + "connection",
            side_effect=AssertionError("socket"),
        ):
            result = joint.sample_once_safe(save=False)
        ok = result.get("disabled") is True and motion._serial is None and spectrum._socket is None
        if ok:
            report.pass_check("no_connection_when_disabled")
        else:
            report.fail_check("no_connection_when_disabled", str(result))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("no_connection_when_disabled", str(exc))
    finally:
        if env_backup is not None:
            os.environ["NFS_ENABLE_REAL_HARDWARE"] = env_backup


def check_fake_adapter_joint_sample(report: verification_report.VerificationReport) -> None:
    report.start_check("fake_adapter_joint_sample")
    env_backup = os.environ.get("NFS_ENABLE_REAL_HARDWARE")
    os.environ["NFS_ENABLE_REAL_HARDWARE"] = "1"
    try:
        verification_runtime.enter_release_runtime("R041")
        from nfs_scanner_pro.devices.real.joint_sample_adapter import JointSampleAdapter

        motion = FakeMotionAdapter()
        spectrum = FakeSpectrumAdapter()
        joint = JointSampleAdapter(motion, spectrum)
        result = joint.sample_once_safe(save=True)
        record = result.get("record", {})
        json_path = Path(str(result.get("json_path", "")))
        csv_path = Path(str(result.get("csv_path", "")))
        r041_in_path = "R041" in json_path.as_posix() and "joint_samples" in json_path.as_posix()
        ok = (
            result.get("ok") is True
            and record.get("position", {}).get("x") == 45.2
            and record.get("spectrum", {}).get("amplitude_dbm") == -23.45
            and record.get("motion_command_executed") is False
            and record.get("sweep_started") is False
            and motion.connect_calls >= 1
            and spectrum.connect_calls >= 1
            and motion.disconnect_calls >= 1
            and spectrum.disconnect_calls >= 1
            and json_path.is_file()
            and csv_path.is_file()
            and r041_in_path
        )
        if ok:
            report.pass_check("fake_adapter_joint_sample")
        else:
            report.fail_check("fake_adapter_joint_sample", str(result))
    except Exception as exc:  # noqa: BLE001
        report.fail_check("fake_adapter_joint_sample", str(exc))
    finally:
        if env_backup is None:
            os.environ.pop("NFS_ENABLE_REAL_HARDWARE", None)
        else:
            os.environ["NFS_ENABLE_REAL_HARDWARE"] = env_backup


def check_real_device_manager_joint_status(report: verification_report.VerificationReport) -> None:
    report.start_check("real_device_manager_joint_status")
    env_backup = os.environ.pop("NFS_ENABLE_REAL_HARDWARE", None)
    try:
        from nfs_scanner_pro.devices.real import RealDeviceManager

        manager = RealDeviceManager()
        snapshot = manager.get_snapshot()
        sample = manager.sample_single_point_safe(save=False)
        connect = manager.connect_all_safe()
        joint = snapshot.get("joint_sample", {})
        ok = (
            sample.get("disabled") is True
            and connect.get("status") == "disabled"
            and joint.get("enabled") is False
            and joint.get("safe_mode") is True
        )
        if ok:
            report.pass_check("real_device_manager_joint_status")
        else:
            report.fail_check(
                "real_device_manager_joint_status",
                f"joint={joint} sample={sample}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_device_manager_joint_status", str(exc))
    finally:
        if env_backup is not None:
            os.environ["NFS_ENABLE_REAL_HARDWARE"] = env_backup


def check_check_joint_sample_script_default(report: verification_report.VerificationReport) -> None:
    report.start_check("check_joint_sample_script_default")
    env = os.environ.copy()
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    proc = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT_PATH)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    proc_no_save = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT_PATH), "--no-save"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    text = proc.stdout + proc.stderr
    text2 = proc_no_save.stdout + proc_no_save.stderr
    ok = (
        proc.returncode == 0
        and proc_no_save.returncode == 0
        and "真实设备未启用" in text
        and "NFS_ENABLE_REAL_HARDWARE=1" in text
        and "真实设备未启用" in text2
    )
    if ok:
        report.pass_check("check_joint_sample_script_default")
    else:
        report.fail_check("check_joint_sample_script_default", text[-300:])


def check_source_no_motion_or_sweep_commands(report: verification_report.VerificationReport) -> None:
    report.start_check("source_no_motion_or_sweep_commands")
    hits: list[str] = []
    for path in (JOINT_ADAPTER_PATH, REAL_MANAGER_PATH, CHECK_SCRIPT_PATH):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_EXEC_TOKENS:
            if token in text:
                hits.append(f"{path.name}: {token}")
    if hits:
        report.fail_check("source_no_motion_or_sweep_commands", "; ".join(hits))
    else:
        report.pass_check("source_no_motion_or_sweep_commands")


def check_mock_ui_unchanged(report: verification_report.VerificationReport) -> None:
    report.start_check("mock_ui_unchanged")
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    failures: list[str] = []
    for script in ("029", "040"):
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
        / "docs/product-spec/release/Release_041_Real_Joint_Single_Point_Sample/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_041 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_041.py",
        "python scripts/verify_all.py --only 041",
        "python scripts/check_joint_single_point_sample_safe.py",
        "python scripts/check_real_devices_safe.py",
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
            "## 默认是否连接真实设备",
            "",
            "否",
            "",
            "## 是否执行真实运动",
            "",
            "否",
            "",
            "## 是否启动 sweep",
            "",
            "否",
            "",
            "## 是否读取完整 Trace",
            "",
            "否",
            "",
            "## 是否支持 JSON / CSV 单点样本保存",
            "",
            "是（仅显式 --save 且 NFS_ENABLE_REAL_HARDWARE=1）",
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
    verification_runtime.enter_release_runtime("R041")
    report = verification_report.VerificationReport("041")

    check_compileall(report)
    check_joint_sample_imports(report)
    check_default_real_hardware_disabled(report)
    check_sample_record_builder(report)
    check_sample_json_csv_persistence(report)
    check_no_connection_when_disabled(report)
    check_fake_adapter_joint_sample(report)
    check_real_device_manager_joint_status(report)
    check_check_joint_sample_script_default(report)
    check_source_no_motion_or_sweep_commands(report)
    check_mock_ui_unchanged(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
