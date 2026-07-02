"""联调 session 持久化 — Release 048。"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nfs_scanner_pro.app_paths import get_runtime_dir
from nfs_scanner_pro.hardware_commissioning.commissioning_model import (
    CommissioningGate,
    CommissioningSession,
    CommissioningStage,
    CommissioningStep,
)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


CSV_FIELDS = (
    "step_id",
    "stage_id",
    "name",
    "required",
    "mode",
    "status",
    "risk_level",
    "manual_confirm_required",
    "real_hardware_required",
    "started_at",
    "finished_at",
    "pass_criteria",
    "actual_result",
    "fail_reason",
    "message",
)


def session_dir(session_id: str, base: Path | None = None) -> Path:
    root = base if base is not None else get_runtime_dir() / "commissioning_sessions"
    path = root / session_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_session(session: CommissioningSession, base: Path | None = None) -> dict[str, Path]:
    directory = session_dir(session.session_id, base)
    json_path = directory / "commissioning_session.json"
    csv_path = directory / "commissioning_steps.csv"
    summary_path = directory / "commissioning_summary.json"
    md_path = directory / "commissioning_report.md"
    failure_path = directory / "failure_records.jsonl"

    session.updated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    save_summary(session, base=base)
    json_path.write_text(
        json.dumps(_json_safe(session.as_dict()), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for step in session.steps:
            writer.writerow(
                {
                    "step_id": step.step_id,
                    "stage_id": step.stage_id,
                    "name": step.name,
                    "required": step.required,
                    "mode": step.mode,
                    "status": step.status,
                    "risk_level": step.risk_level,
                    "manual_confirm_required": step.manual_confirm_required,
                    "real_hardware_required": step.real_hardware_required,
                    "started_at": step.started_at,
                    "finished_at": step.finished_at,
                    "pass_criteria": step.pass_criteria,
                    "actual_result": json.dumps(_json_safe(step.actual_result), ensure_ascii=False),
                    "fail_reason": step.fail_reason,
                    "message": step.message,
                }
            )
    export_markdown_report(session, path=md_path)
    if session.failure_records:
        with failure_path.open("w", encoding="utf-8") as handle:
            for record in session.failure_records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {
        "session_json": json_path,
        "steps_csv": csv_path,
        "summary_json": summary_path,
        "report_md": md_path,
        "failure_jsonl": failure_path,
    }


def save_summary(session: CommissioningSession, base: Path | None = None) -> Path:
    directory = session_dir(session.session_id, base)
    summary_path = directory / "commissioning_summary.json"
    payload = {
        "session_id": session.session_id,
        "workflow_name": session.workflow_name,
        "mode": session.mode,
        "total_steps": session.total_steps(),
        "passed_steps": session.passed_steps(),
        "failed_steps": session.failed_steps(),
        "blocked_steps": session.blocked_steps(),
        "completion_ratio": session.completion_ratio(),
        "ready_for_real_run": session.is_ready_for_real_run(),
        "real_hardware_enabled": session.real_hardware_enabled,
        "safe_mode": session.safe_mode,
        "real_run_allowed": session.real_run_allowed,
        "gate": session.gate.as_dict(),
    }
    session.summary = payload
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary_path


def load_session(path: str | Path) -> CommissioningSession:
    json_path = Path(path)
    if json_path.is_dir():
        json_path = json_path / "commissioning_session.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    steps = [
        CommissioningStep(**{k: v for k, v in item.items() if k in CommissioningStep.__dataclass_fields__})
        for item in data.get("steps", [])
    ]
    stages = [
        CommissioningStage(
            stage_id=item["stage_id"],
            name=item["name"],
            required=item.get("required", True),
            real_hardware_required=item.get("real_hardware_required", False),
            manual_confirm_required=item.get("manual_confirm_required", False),
            risk_level=item.get("risk_level", "low"),
            steps=[s for s in steps if s.stage_id == item["stage_id"]],
        )
        for item in data.get("stages", [])
    ]
    gate_data = data.get("gate", {})
    return CommissioningSession(
        session_id=data["session_id"],
        workflow_name=data["workflow_name"],
        mode=data["mode"],
        hardware_mode=data.get("hardware_mode", "mock"),
        created_at=data["created_at"],
        updated_at=data.get("updated_at", data["created_at"]),
        operator=data.get("operator", ""),
        stages=stages,
        steps=steps,
        summary=data.get("summary", {}),
        artifacts=data.get("artifacts", {}),
        safe_mode=data.get("safe_mode", True),
        real_hardware_enabled=data.get("real_hardware_enabled", False),
        real_run_allowed=data.get("real_run_allowed", False),
        failure_records=data.get("failure_records", []),
        gate=CommissioningGate(**{k: v for k, v in gate_data.items() if k in CommissioningGate.__dataclass_fields__}),
    )


def append_failure_record(session: CommissioningSession, step: CommissioningStep, reason: str) -> None:
    record = {
        "step_id": step.step_id,
        "stage_id": step.stage_id,
        "name": step.name,
        "reason": reason,
        "timestamp_iso": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    session.failure_records.append(record)


def export_markdown_report(session: CommissioningSession, path: Path | None = None) -> str:
    lines = [
        "# 硬件现场联调报告",
        "",
        f"- Session: `{session.session_id}`",
        f"- Workflow: {session.workflow_name}",
        f"- Mode: **{session.mode}**",
        f"- Hardware mode: {session.hardware_mode}",
        f"- Passed: {session.passed_steps()} / {session.total_steps()}",
        f"- Ready for real-run: **{session.is_ready_for_real_run()}**",
        "",
        "## 步骤结果",
        "",
        "| Step | Status | Message |",
        "|------|--------|---------|",
    ]
    for step in session.steps:
        lines.append(f"| {step.name} | {step.status} | {step.message[:60]} |")
    lines.extend(
        [
            "",
            "## Real-run Gate",
            "",
            f"- Allowed: {session.real_run_allowed}",
            f"- Blocked reasons: {', '.join(session.gate.blocked_reasons) or '—'}",
            "",
            "> 本报告不表示已执行真实扫描。",
        ]
    )
    text = "\n".join(lines)
    if path is not None:
        path.write_text(text, encoding="utf-8")
    return text
