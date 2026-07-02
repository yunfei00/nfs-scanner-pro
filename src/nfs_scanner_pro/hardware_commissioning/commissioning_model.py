"""联调数据模型 — Release 048。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CommissioningResult:
    ok: bool
    status: str
    message: str = ""
    actual_result: dict[str, Any] = field(default_factory=dict)
    fail_reason: str = ""
    artifacts: dict[str, Any] = field(default_factory=dict)
    pass_criteria: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CommissioningGate:
    ready: bool = False
    blocked_reasons: list[str] = field(default_factory=list)
    required_checks: dict[str, bool] = field(default_factory=dict)
    manual_confirm_complete: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CommissioningStep:
    step_id: str
    stage_id: str
    name: str
    description: str = ""
    required: bool = True
    mode: str = "offline"
    status: str = "pending"
    started_at: str = ""
    finished_at: str = ""
    command: str = ""
    expected_result: str = ""
    actual_result: dict[str, Any] = field(default_factory=dict)
    pass_criteria: str = ""
    fail_reason: str = ""
    manual_confirm_required: bool = False
    real_hardware_required: bool = False
    risk_level: str = "low"
    artifacts: dict[str, Any] = field(default_factory=dict)
    message: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CommissioningStage:
    stage_id: str
    name: str
    required: bool = True
    real_hardware_required: bool = False
    manual_confirm_required: bool = False
    risk_level: str = "low"
    steps: list[CommissioningStep] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["steps"] = [step.as_dict() for step in self.steps]
        return data


@dataclass
class CommissioningSession:
    session_id: str
    workflow_name: str
    mode: str
    hardware_mode: str
    created_at: str
    updated_at: str
    operator: str = ""
    stages: list[CommissioningStage] = field(default_factory=list)
    steps: list[CommissioningStep] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)
    safe_mode: bool = True
    real_hardware_enabled: bool = False
    real_run_allowed: bool = False
    failure_records: list[dict[str, Any]] = field(default_factory=list)
    gate: CommissioningGate = field(default_factory=CommissioningGate)

    def total_steps(self) -> int:
        return len(self.steps)

    def passed_steps(self) -> int:
        return sum(1 for step in self.steps if step.status == "passed")

    def failed_steps(self) -> int:
        return sum(1 for step in self.steps if step.status == "failed")

    def blocked_steps(self) -> int:
        return sum(1 for step in self.steps if step.status == "blocked")

    def completion_ratio(self) -> float:
        total = self.total_steps()
        if total == 0:
            return 0.0
        return round(self.passed_steps() / total, 4)

    def is_ready_for_real_run(self) -> bool:
        return self.real_run_allowed and self.gate.ready

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "workflow_name": self.workflow_name,
            "mode": self.mode,
            "hardware_mode": self.hardware_mode,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "operator": self.operator,
            "stages": [stage.as_dict() for stage in self.stages],
            "steps": [step.as_dict() for step in self.steps],
            "summary": self.summary,
            "artifacts": self.artifacts,
            "safe_mode": self.safe_mode,
            "real_hardware_enabled": self.real_hardware_enabled,
            "real_run_allowed": self.real_run_allowed,
            "failure_records": list(self.failure_records),
            "gate": self.gate.as_dict(),
            "total_steps": self.total_steps(),
            "passed_steps": self.passed_steps(),
            "failed_steps": self.failed_steps(),
            "blocked_steps": self.blocked_steps(),
            "completion_ratio": self.completion_ratio(),
            "ready_for_real_run": self.is_ready_for_real_run(),
        }
