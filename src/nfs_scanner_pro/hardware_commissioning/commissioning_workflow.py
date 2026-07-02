"""联调 workflow 加载与 session 构建 — Release 048。"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from nfs_scanner_pro.app_paths import get_project_root
from nfs_scanner_pro.devices.hardware_mode import get_hardware_mode
from nfs_scanner_pro.devices.real.hardware_config import is_real_hardware_enabled
from nfs_scanner_pro.hardware_commissioning.commissioning_model import (
    CommissioningSession,
    CommissioningStage,
    CommissioningStep,
)

DEFAULT_STAGES: tuple[dict[str, Any], ...] = (
    {"id": "env_check", "name": "环境检查", "required": True, "real_hardware_required": False, "risk_level": "low"},
    {"id": "config_check", "name": "配置检查", "required": True, "real_hardware_required": False, "risk_level": "low"},
    {"id": "motion_status", "name": "运动平台状态读取", "required": True, "real_hardware_required": True, "risk_level": "low"},
    {
        "id": "motion_jog",
        "name": "运动平台小步点动",
        "required": True,
        "real_hardware_required": True,
        "manual_confirm_required": True,
        "risk_level": "high",
    },
    {"id": "spectrum_idn", "name": "频谱仪 IDN 查询", "required": True, "real_hardware_required": True, "risk_level": "low"},
    {
        "id": "spectrum_marker",
        "name": "频谱仪 Marker 幅度读取",
        "required": True,
        "real_hardware_required": True,
        "risk_level": "low",
    },
    {"id": "camera_list", "name": "相机枚举", "required": False, "real_hardware_required": True, "risk_level": "low"},
    {
        "id": "camera_capture",
        "name": "相机拍照",
        "required": False,
        "real_hardware_required": True,
        "manual_confirm_required": True,
        "risk_level": "medium",
    },
    {"id": "servo_state", "name": "舵机状态读取", "required": False, "real_hardware_required": True, "risk_level": "low"},
    {
        "id": "servo_switch",
        "name": "舵机 Hx Hy 切换",
        "required": False,
        "real_hardware_required": True,
        "manual_confirm_required": True,
        "risk_level": "high",
    },
    {
        "id": "joint_sample",
        "name": "当前位置与频谱单点联合采样",
        "required": True,
        "real_hardware_required": True,
        "manual_confirm_required": True,
        "risk_level": "medium",
    },
    {"id": "scan_plan_dry_run", "name": "3x3 扫描计划 Dry Run", "required": True, "real_hardware_required": False, "risk_level": "low"},
    {"id": "scan_fake_run", "name": "3x3 扫描 Fake Run", "required": True, "real_hardware_required": False, "risk_level": "low"},
    {"id": "real_run_gate", "name": "真实扫描执行门禁", "required": True, "real_hardware_required": False, "risk_level": "high"},
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_yaml(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return None


def build_default_workflow() -> dict[str, Any]:
    return {
        "workflow_name": "nfs-scanner-real-hardware-commissioning",
        "version": "1.0",
        "default_mode": "offline",
        "stages": [dict(stage) for stage in DEFAULT_STAGES],
        "source": "builtin",
    }


def load_commissioning_workflow(path: str | Path | None = None) -> dict[str, Any]:
    if path is not None:
        data = _load_yaml(Path(path))
        if data and data.get("stages"):
            data["source"] = str(path)
            return data
    local = get_project_root() / "config" / "commissioning.local.yaml"
    data = _load_yaml(local)
    if data and data.get("stages"):
        data["source"] = str(local)
        return data
    example = get_project_root() / "config" / "commissioning.workflow.example.yaml"
    data = _load_yaml(example)
    if data and data.get("stages"):
        data["source"] = str(example)
        return data
    return build_default_workflow()


def validate_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    stages = workflow.get("stages") or []
    ids = [stage.get("id") for stage in stages]
    required_ids = {
        "env_check",
        "motion_status",
        "spectrum_idn",
        "joint_sample",
        "scan_fake_run",
        "real_run_gate",
    }
    missing = sorted(required_ids - {stage_id for stage_id in ids if stage_id})
    ok = not missing and bool(stages)
    return {
        "ok": ok,
        "stage_count": len(stages),
        "missing_stage_ids": missing,
        "workflow_name": workflow.get("workflow_name", ""),
        "version": workflow.get("version", ""),
    }


def build_session_from_workflow(workflow: dict[str, Any], mode: str = "offline") -> CommissioningSession:
    session_id = f"CM-{uuid4().hex[:8].upper()}"
    now = _now_iso()
    stages: list[CommissioningStage] = []
    steps: list[CommissioningStep] = []
    for raw in workflow.get("stages", []):
        stage_id = str(raw.get("id", ""))
        step = CommissioningStep(
            step_id=stage_id,
            stage_id=stage_id,
            name=str(raw.get("name", stage_id)),
            description=str(raw.get("description", raw.get("name", stage_id))),
            required=bool(raw.get("required", True)),
            mode=mode,
            manual_confirm_required=bool(raw.get("manual_confirm_required", False)),
            real_hardware_required=bool(raw.get("real_hardware_required", False)),
            risk_level=str(raw.get("risk_level", "low")),
            pass_criteria="按阶段验收标准 PASS",
        )
        stage = CommissioningStage(
            stage_id=stage_id,
            name=step.name,
            required=step.required,
            real_hardware_required=step.real_hardware_required,
            manual_confirm_required=step.manual_confirm_required,
            risk_level=step.risk_level,
            steps=[step],
        )
        stages.append(stage)
        steps.append(step)
    return CommissioningSession(
        session_id=session_id,
        workflow_name=str(workflow.get("workflow_name", "commissioning")),
        mode=mode,
        hardware_mode=get_hardware_mode().value,
        created_at=now,
        updated_at=now,
        stages=stages,
        steps=steps,
        safe_mode=True,
        real_hardware_enabled=is_real_hardware_enabled(),
        real_run_allowed=False,
    )
