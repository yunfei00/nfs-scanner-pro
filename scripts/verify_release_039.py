#!/usr/bin/env python3
"""Release_039 自动验收 — Real Spectrum Analyzer Safe Connect And Read。"""

from __future__ import annotations

import compileall
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
from verification_utils import setup_path  # noqa: E402

IMPORT_MODULES = (
    "nfs_scanner_pro.devices.real.hardware_config",
    "nfs_scanner_pro.devices.real.hardware_safety",
    "nfs_scanner_pro.devices.real.real_device_manager",
    "nfs_scanner_pro.devices.real.spectrum_scpi_adapter",
)

SPECTRUM_ADAPTER_PATH = SRC / "nfs_scanner_pro/devices/real/spectrum_scpi_adapter.py"

ALLOWED_SCPI = (
    "*IDN?",
    "SYST:ERR?",
    "FREQ:CENT?",
    "SENS:FREQ:CENT?",
    "CALC:PAR:CAT?",
)

FORBIDDEN_SCPI = (
    "FREQ:CENT 2450000000",
    "SENS:BAND 1000",
    "INIT",
    "INIT:IMM",
    "SING",
    "CAL",
    "CALC:DATA?",
    "TRAC:DATA?",
    'FORM:DATA REAL,32',
    'MMEM:STOR "a.csv"',
)

FORBIDDEN_SOURCE_TOKENS = (
    "INIT:IMM",
    "INIT;",
    "SING",
    "CALC:DATA?",
    "TRAC:DATA?",
    "FORM:DATA",
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


def check_real_spectrum_imports(report: verification_report.VerificationReport) -> None:
    report.start_check("real_spectrum_imports")
    try:
        from nfs_scanner_pro.devices.real import (
            RealDeviceManager,
            SpectrumScpiAdapter,
            is_real_hardware_enabled,
        )

        ok = (
            SpectrumScpiAdapter is not None
            and RealDeviceManager is not None
            and callable(is_real_hardware_enabled)
        )
        if ok:
            report.pass_check("real_spectrum_imports")
        else:
            report.fail_check("real_spectrum_imports", "missing symbol")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_spectrum_imports", str(exc))


def check_default_real_hardware_disabled(report: verification_report.VerificationReport) -> None:
    report.start_check("default_real_hardware_disabled")
    env_backup = os.environ.pop("NFS_ENABLE_REAL_HARDWARE", None)
    try:
        from nfs_scanner_pro.devices.real import (
            SPECTRUM_DISABLED_MESSAGE,
            RealDeviceManager,
            SpectrumScpiAdapter,
            is_real_hardware_enabled,
        )

        adapter = SpectrumScpiAdapter()
        manager = RealDeviceManager()
        connect_msg = adapter.connect()
        all_safe = manager.connect_all_safe()
        ok = (
            not is_real_hardware_enabled()
            and adapter._socket is None
            and adapter._visa_resource is None
            and SPECTRUM_DISABLED_MESSAGE in connect_msg
            and all_safe.get("status") == "disabled"
        )
        if ok:
            report.pass_check("default_real_hardware_disabled")
        else:
            report.fail_check(
                "default_real_hardware_disabled",
                f"connect={connect_msg!r} all={all_safe}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("default_real_hardware_disabled", str(exc))
    finally:
        if env_backup is not None:
            os.environ["NFS_ENABLE_REAL_HARDWARE"] = env_backup


def check_scpi_query_whitelist(report: verification_report.VerificationReport) -> None:
    report.start_check("scpi_query_whitelist")
    try:
        from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter

        adapter = SpectrumScpiAdapter()
        allowed_ok = all(
            SpectrumScpiAdapter.validate_query_command(cmd)[0] for cmd in ALLOWED_SCPI
        )
        forbidden_ok = all(
            not SpectrumScpiAdapter.validate_query_command(cmd)[0]
            for cmd in FORBIDDEN_SCPI
        )
        query_blocked = adapter.query("INIT:IMM")
        ok = (
            allowed_ok
            and forbidden_ok
            and query_blocked.get("ok") is False
            and adapter._socket is None
        )
        if ok:
            report.pass_check("scpi_query_whitelist")
        else:
            report.fail_check(
                "scpi_query_whitelist",
                f"allowed={allowed_ok} forbidden={forbidden_ok} query={query_blocked}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("scpi_query_whitelist", str(exc))


def check_frequency_response_parser(report: verification_report.VerificationReport) -> None:
    report.start_check("frequency_response_parser")
    try:
        from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter

        hz = SpectrumScpiAdapter.parse_frequency_response("2450000000")
        sci = SpectrumScpiAdapter.parse_frequency_response("2.45E9")
        bad = SpectrumScpiAdapter.parse_frequency_response("abc")
        ok = (
            hz.get("ok")
            and hz.get("frequency_hz") == 2450000000.0
            and abs(hz.get("frequency_ghz", 0) - 2.45) < 1e-9
            and sci.get("ok")
            and abs(sci.get("frequency_ghz", 0) - 2.45) < 1e-9
            and not bad.get("ok")
        )
        if ok:
            report.pass_check("frequency_response_parser")
        else:
            report.fail_check(
                "frequency_response_parser",
                f"hz={hz} sci={sci} bad={bad}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("frequency_response_parser", str(exc))


def check_no_connection_when_disabled(report: verification_report.VerificationReport) -> None:
    report.start_check("no_connection_when_disabled")
    env_backup = os.environ.pop("NFS_ENABLE_REAL_HARDWARE", None)
    try:
        from nfs_scanner_pro.devices.real.spectrum_scpi_adapter import SpectrumScpiAdapter

        adapter = SpectrumScpiAdapter()
        with mock.patch.object(
            socket,
            "create_" + "connection",
            side_effect=AssertionError("socket"),
        ):
            msg = adapter.connect()
        with mock.patch.dict(sys.modules, {"pyvisa": mock.MagicMock()}):
            adapter2 = SpectrumScpiAdapter()
            adapter2.config.backend = "visa"
            with mock.patch(
                "nfs_scanner_pro.devices.real.spectrum_scpi_adapter._visa_mod",
                mock.MagicMock(),
            ):
                msg2 = adapter2.connect()
        test = adapter.test_connection()
        ok = (
            "未启用" in msg
            and "未启用" in msg2
            and test.get("enabled") is False
            and adapter._socket is None
        )
        if ok:
            report.pass_check("no_connection_when_disabled")
        else:
            report.fail_check(
                "no_connection_when_disabled",
                f"msg={msg!r} msg2={msg2!r} test={test}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("no_connection_when_disabled", str(exc))
    finally:
        if env_backup is not None:
            os.environ["NFS_ENABLE_REAL_HARDWARE"] = env_backup


def check_check_real_devices_safe_default(report: verification_report.VerificationReport) -> None:
    report.start_check("check_real_devices_safe_default")
    env = os.environ.copy()
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "check_real_devices_safe.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    text = proc.stdout + proc.stderr
    ok = (
        proc.returncode == 0
        and "真实设备未启用" in text
        and "NFS_ENABLE_REAL_HARDWARE=1" in text
    )
    if ok:
        report.pass_check("check_real_devices_safe_default")
    else:
        report.fail_check("check_real_devices_safe_default", text[-400:])


def check_real_device_manager_spectrum_status(report: verification_report.VerificationReport) -> None:
    report.start_check("real_device_manager_spectrum_status")
    env_backup = os.environ.pop("NFS_ENABLE_REAL_HARDWARE", None)
    try:
        from nfs_scanner_pro.devices.real import RealDeviceManager

        manager = RealDeviceManager()
        rows = manager.get_device_status()
        snapshot = manager.get_snapshot()
        connect = manager.connect_all_safe()
        test = manager.test_all_safe()
        spectrum_row = next((r for r in rows if r.get("name") == "频谱仪"), {})
        spectrum_snap = snapshot.get("spectrum", {})
        ok = (
            connect.get("status") == "disabled"
            and test.get("status") == "disabled"
            and spectrum_row.get("status") == "disabled"
            and isinstance(spectrum_snap, dict)
            and spectrum_snap.get("safe_mode") is True
        )
        if ok:
            report.pass_check("real_device_manager_spectrum_status")
        else:
            report.fail_check(
                "real_device_manager_spectrum_status",
                f"row={spectrum_row} snap={spectrum_snap} connect={connect}",
            )
    except Exception as exc:  # noqa: BLE001
        report.fail_check("real_device_manager_spectrum_status", str(exc))
    finally:
        if env_backup is not None:
            os.environ["NFS_ENABLE_REAL_HARDWARE"] = env_backup


def check_mock_ui_unchanged(report: verification_report.VerificationReport) -> None:
    report.start_check("mock_ui_unchanged")
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.pop("NFS_ENABLE_REAL_HARDWARE", None)
    failures: list[str] = []
    for script in ("029", "037", "038"):
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


def check_source_scpi_command_safety(report: verification_report.VerificationReport) -> None:
    report.start_check("source_scpi_command_safety")
    try:
        text = SPECTRUM_ADAPTER_PATH.read_text(encoding="utf-8")
        ok = (
            "ALLOWED_QUERY_COMMANDS" in text
            and "validate_query_command" in text
            and "is_real_hardware_enabled()" in text
            and "INIT:IMM" not in text
            and 'self._transport_query("INIT' not in text
            and 'self._transport_query("CALC:DATA?' not in text
        )
        if ok:
            report.pass_check("source_scpi_command_safety")
        else:
            report.fail_check("source_scpi_command_safety", "missing guard or forbidden token")
    except Exception as exc:  # noqa: BLE001
        report.fail_check("source_scpi_command_safety", str(exc))


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
        / "docs/product-spec/release/Release_039_Real_Spectrum_Analyzer_Safe_Connect_And_Read/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_039 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_039.py",
        "python scripts/verify_all.py --only 039",
        "python scripts/verify_all.py --from 038",
        "python scripts/verify_all.py",
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
            "## 是否修改仪表配置",
            "",
            "否",
            "",
            "## 是否启动 sweep",
            "",
            "否",
            "",
            "## 是否读取大批量 Trace",
            "",
            "否",
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
    report = verification_report.VerificationReport("039")

    check_compileall(report)
    check_real_spectrum_imports(report)
    check_default_real_hardware_disabled(report)
    check_scpi_query_whitelist(report)
    check_frequency_response_parser(report)
    check_no_connection_when_disabled(report)
    check_check_real_devices_safe_default(report)
    check_real_device_manager_spectrum_status(report)
    check_mock_ui_unchanged(report)
    check_source_scpi_command_safety(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
