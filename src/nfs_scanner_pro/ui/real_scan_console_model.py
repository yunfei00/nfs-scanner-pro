"""真实扫描控制台数据模型 — Release 046（无 Qt / 无设备）。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RealScanConsoleModel:
    hardware_mode: str = "mock"
    plan_path: str = ""
    plan_summary: dict[str, Any] = field(default_factory=dict)
    execution_mode: str = "dry_run"
    progress: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)
    output_paths: dict[str, str] = field(default_factory=dict)
    real_run_enabled: bool = False
    safe_message: str = ""
    scan_state: str = "idle"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def reset(self) -> None:
        self.plan_path = ""
        self.plan_summary = {}
        self.progress = {}
        self.logs = []
        self.output_paths = {}
        self.scan_state = "idle"

    def append_log(self, message: str) -> None:
        text = str(message).strip()
        if text:
            self.logs.append(text)

    def set_plan(self, plan_summary: dict[str, Any], path: str = "") -> None:
        self.plan_summary = dict(plan_summary)
        self.plan_path = path

    def set_progress(self, progress: dict[str, Any]) -> None:
        self.progress = dict(progress)
        if progress.get("state"):
            self.scan_state = str(progress["state"])

    def set_outputs(self, paths: dict[str, str | Any]) -> None:
        self.output_paths = {key: str(value) for key, value in paths.items()}
