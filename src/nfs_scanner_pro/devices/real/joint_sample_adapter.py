"""联合单点采样 — 运动位置 + 频谱 Marker 幅度（Release 041）。"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from nfs_scanner_pro.app_paths import get_runtime_dir
from nfs_scanner_pro.devices.real.hardware_config import (
    DISABLED_MESSAGE,
    is_real_hardware_enabled,
)

CSV_FIELDS = (
    "sample_id",
    "timestamp_iso",
    "project_name",
    "task_id",
    "x",
    "y",
    "z",
    "position_source",
    "motion_state",
    "frequency_hz",
    "frequency_ghz",
    "amplitude_dbm",
    "unit",
    "spectrum_source",
    "motion_command_executed",
    "sweep_started",
    "safe_mode",
)


class JointSampleAdapter:
    TASK_ID = "MANUAL-SINGLE-POINT"
    DEFAULT_PROJECT = "Manual_Check"

    def __init__(
        self,
        motion_adapter: Any,
        spectrum_adapter: Any,
        output_dir: Path | str | None = None,
    ) -> None:
        self.motion = motion_adapter
        self.spectrum = spectrum_adapter
        self.output_dir = Path(output_dir) if output_dir is not None else None
        self._last_sample: dict[str, Any] | None = None
        self._last_json_path: Path | None = None
        self._last_csv_path: Path | None = None

    def sample_once(self, *, save: bool = False) -> dict[str, Any]:
        return self.sample_once_safe(save=save)

    def sample_once_safe(self, *, save: bool = False) -> dict[str, Any]:
        if not is_real_hardware_enabled():
            outcome = {
                "ok": False,
                "disabled": True,
                "error": DISABLED_MESSAGE,
                "motion_command_executed": False,
                "sweep_started": False,
            }
            self._last_sample = dict(outcome)
            return outcome

        motion_connected = False
        spectrum_connected = False
        outcome: dict[str, Any] = {
            "ok": False,
            "enabled": True,
            "motion_command_executed": False,
            "sweep_started": False,
            "save": save,
        }
        try:
            if self.motion is None:
                outcome["error"] = "运动平台 Adapter 不可用"
                return outcome
            if self.spectrum is None:
                outcome["error"] = "频谱仪 Adapter 不可用"
                return outcome

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

            record = self.build_sample_record(position, marker)
            outcome["record"] = record
            outcome["ok"] = True
            self._last_sample = record

            if save:
                json_path = self.save_sample_json(record)
                csv_path = self.save_sample_csv(record)
                outcome["json_path"] = str(json_path)
                outcome["csv_path"] = str(csv_path)
            return outcome
        except Exception as exc:  # noqa: BLE001
            outcome["error"] = str(exc)
            return outcome
        finally:
            if spectrum_connected and hasattr(self.spectrum, "is_connected"):
                try:
                    if self.spectrum.is_connected():
                        outcome["spectrum_disconnect"] = self.spectrum.disconnect()
                except Exception:  # noqa: BLE001
                    pass
            if motion_connected and hasattr(self.motion, "is_connected"):
                try:
                    if self.motion.is_connected():
                        outcome["motion_disconnect"] = self.motion.disconnect()
                except Exception:  # noqa: BLE001
                    pass

    def build_sample_record(
        self,
        motion_position: dict[str, Any],
        spectrum_amplitude: dict[str, Any],
    ) -> dict[str, Any]:
        project_name = self._resolve_project_name()
        sample_id = f"SP-{uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return {
            "sample_id": sample_id,
            "timestamp_iso": timestamp,
            "project_name": project_name,
            "task_id": self.TASK_ID,
            "position": {
                "x": float(motion_position.get("x", 0.0)),
                "y": float(motion_position.get("y", 0.0)),
                "z": float(motion_position.get("z", 0.0)),
                "source": str(motion_position.get("source", "")),
                "state": str(
                    motion_position.get("state", "")
                    or getattr(self.motion, "grbl_state", "")
                ),
            },
            "spectrum": {
                "frequency_hz": spectrum_amplitude.get("frequency_hz"),
                "frequency_ghz": spectrum_amplitude.get("frequency_ghz"),
                "amplitude_dbm": spectrum_amplitude.get("amplitude_dbm"),
                "unit": spectrum_amplitude.get("unit", "dBm"),
                "source": spectrum_amplitude.get("source", "marker"),
                "raw": str(spectrum_amplitude.get("raw", "")),
            },
            "safe_mode": True,
            "real_hardware": True,
            "motion_command_executed": False,
            "sweep_started": False,
        }

    def save_sample_json(
        self,
        record: dict[str, Any],
        path: Path | str | None = None,
    ) -> Path:
        target = Path(path) if path is not None else self._sample_dir(record) / "single_point_sample.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._last_json_path = target
        return target

    def save_sample_csv(
        self,
        record: dict[str, Any],
        path: Path | str | None = None,
    ) -> Path:
        target = Path(path) if path is not None else self._sample_dir(record) / "single_point_sample.csv"
        target.parent.mkdir(parents=True, exist_ok=True)
        position = record.get("position", {})
        spectrum = record.get("spectrum", {})
        row = {
            "sample_id": record.get("sample_id", ""),
            "timestamp_iso": record.get("timestamp_iso", ""),
            "project_name": record.get("project_name", ""),
            "task_id": record.get("task_id", ""),
            "x": position.get("x", ""),
            "y": position.get("y", ""),
            "z": position.get("z", ""),
            "position_source": position.get("source", ""),
            "motion_state": position.get("state", ""),
            "frequency_hz": spectrum.get("frequency_hz", ""),
            "frequency_ghz": spectrum.get("frequency_ghz", ""),
            "amplitude_dbm": spectrum.get("amplitude_dbm", ""),
            "unit": spectrum.get("unit", ""),
            "spectrum_source": spectrum.get("source", ""),
            "motion_command_executed": record.get("motion_command_executed", False),
            "sweep_started": record.get("sweep_started", False),
            "safe_mode": record.get("safe_mode", True),
        }
        with target.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerow(row)
        self._last_csv_path = target
        return target

    def snapshot(self) -> dict[str, Any]:
        if not is_real_hardware_enabled():
            return {
                "enabled": False,
                "last_sample": {"disabled": True},
                "safe_mode": True,
            }
        last = self._last_sample if self._last_sample is not None else None
        return {
            "enabled": True,
            "last_sample": last,
            "safe_mode": True,
            "json_path": str(self._last_json_path) if self._last_json_path else "",
            "csv_path": str(self._last_csv_path) if self._last_csv_path else "",
        }

    def _sample_dir(self, record: dict[str, Any]) -> Path:
        sample_id = str(record.get("sample_id", "SP-UNKNOWN"))
        base = self.output_dir if self.output_dir is not None else get_runtime_dir() / "joint_samples"
        return base / sample_id

    @staticmethod
    def _resolve_project_name() -> str:
        try:
            from nfs_scanner_pro import project_mock

            name = project_mock.get_scan_project_name()
            if name and name not in ("", "未打开项目"):
                return name
        except Exception:  # noqa: BLE001
            pass
        return JointSampleAdapter.DEFAULT_PROJECT
