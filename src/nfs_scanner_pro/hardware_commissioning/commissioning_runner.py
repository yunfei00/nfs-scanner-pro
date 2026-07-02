"""联调执行器 — Release 048。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from nfs_scanner_pro.devices.hardware_mode import get_hardware_mode
from nfs_scanner_pro.devices.real.hardware_config import is_real_hardware_enabled
from nfs_scanner_pro.hardware_commissioning import commissioning_checks as checks
from nfs_scanner_pro.hardware_commissioning.commissioning_model import (
    CommissioningResult,
    CommissioningSession,
    CommissioningStep,
)
from nfs_scanner_pro.hardware_commissioning.commissioning_persistence import append_failure_record
from nfs_scanner_pro.hardware_commissioning.commissioning_workflow import (
    build_session_from_workflow,
    load_commissioning_workflow,
)

STEP_HANDLERS: dict[str, Callable[..., CommissioningResult]] = {
    "env_check": checks.check_environment,
    "config_check": checks.check_config_files,
    "scan_plan_dry_run": checks.check_scan_dry_run_offline,
    "scan_fake_run": checks.check_scan_fake_run_offline,
}


class CommissioningRunner:
    def __init__(self, session: CommissioningSession | None = None, workflow_path: str | None = None) -> None:
        workflow = load_commissioning_workflow(workflow_path)
        self.workflow = workflow
        self.session = session or build_session_from_workflow(workflow, mode="offline")

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _apply_result(self, step: CommissioningStep, result: CommissioningResult) -> None:
        step.status = result.status
        step.message = result.message
        step.fail_reason = result.fail_reason
        step.actual_result = result.actual_result
        step.pass_criteria = result.pass_criteria or step.pass_criteria
        step.artifacts.update(result.artifacts)
        step.finished_at = self._now()
        if result.status == "failed":
            append_failure_record(self.session, step, result.fail_reason or result.message)

    def _run_step(self, step: CommissioningStep) -> CommissioningResult:
        step.status = "running"
        step.started_at = self._now()
        mode = self.session.mode
        fake = mode == "fake"

        if step.manual_confirm_required and mode != "real-safe":
            result = CommissioningResult(
                ok=True,
                status="skipped",
                message="需现场 manual confirm，offline/fake 模式跳过",
            )
            self._apply_result(step, result)
            return result

        if step.real_hardware_required and mode == "offline":
            result = CommissioningResult(
                ok=True,
                status="skipped",
                message="offline 模式跳过真实硬件步骤",
            )
            self._apply_result(step, result)
            return result

        if step.real_hardware_required and mode == "real-safe" and not is_real_hardware_enabled():
            result = checks._blocked("NFS_ENABLE_REAL_HARDWARE 未设置")
            self._apply_result(step, result)
            return result

        handler = STEP_HANDLERS.get(step.step_id)
        if handler is not None:
            result = handler()
        elif step.step_id == "motion_status":
            result = self._device_step_result(step.step_id, fake=fake)
        elif step.step_id == "motion_jog":
            result = CommissioningResult(ok=True, status="skipped", message="点动需 manual confirm + 子开关")
        elif step.step_id == "spectrum_idn":
            result = self._device_step_result(step.step_id, fake=fake)
        elif step.step_id == "spectrum_marker":
            result = self._device_step_result(step.step_id, fake=fake)
        elif step.step_id == "camera_list":
            result = checks.check_camera_status_offline(fake=fake)
        elif step.step_id == "camera_capture":
            result = CommissioningResult(ok=True, status="skipped", message="拍照需 manual confirm")
        elif step.step_id == "servo_state":
            result = checks.check_servo_status_offline(fake=fake)
        elif step.step_id == "servo_switch":
            result = CommissioningResult(ok=True, status="skipped", message="舵机切换需 manual confirm")
        elif step.step_id == "joint_sample":
            result = self._device_step_result("joint_sample", fake=fake)
        elif step.step_id == "real_run_gate":
            result = checks.check_real_run_gate(self.session)
        else:
            result = CommissioningResult(ok=False, status="failed", message=f"未知步骤 {step.step_id}")

        if mode == "real-safe" and step.step_id in ("motion_status", "spectrum_idn", "spectrum_marker"):
            probe = self.session.artifacts.get("real_safe_probe", {})
            if probe.get("status") == "passed":
                result = CommissioningResult(
                    ok=True,
                    status="passed",
                    message="test_all_safe 安全探测已覆盖",
                    actual_result=probe.get("actual_result", {}),
                )
            elif probe:
                result = checks._blocked(probe.get("message", "real-safe blocked"))

        self._apply_result(step, result)
        return result

    def _device_step_result(self, step_id: str, *, fake: bool) -> CommissioningResult:
        mode = self.session.mode
        if mode == "real-safe":
            probe = self.session.artifacts.get("real_safe_probe", {})
            if probe.get("status") == "passed":
                return CommissioningResult(
                    ok=True,
                    status="passed",
                    message="test_all_safe 安全探测已覆盖",
                    actual_result=probe.get("actual_result", {}),
                )
            if probe:
                return checks._blocked(probe.get("message", "real-safe blocked"))
        mapping = {
            "motion_status": lambda: checks.check_motion_status_offline(fake=fake),
            "spectrum_idn": lambda: checks.check_spectrum_status_offline(fake=fake),
            "spectrum_marker": lambda: checks.check_spectrum_marker_offline(fake=fake),
            "joint_sample": lambda: checks.check_joint_sample_offline(fake=fake),
        }
        fn = mapping.get(step_id)
        if fn is None:
            return CommissioningResult(ok=False, status="failed", message=f"未知设备步骤 {step_id}")
        return fn()

    def run_offline(self) -> CommissioningSession:
        self.session.mode = "offline"
        self._run_all()
        return self.session

    def run_fake(self) -> CommissioningSession:
        self.session.mode = "fake"
        self._run_all()
        return self.session

    def run_real_safe(self) -> CommissioningSession:
        self.session.mode = "real-safe"
        self.session.real_hardware_enabled = is_real_hardware_enabled()
        if not is_real_hardware_enabled():
            for step in self.session.steps:
                if step.real_hardware_required:
                    step.status = "blocked"
                    step.message = "NFS_ENABLE_REAL_HARDWARE 未设置"
                    step.started_at = self._now()
                    step.finished_at = self._now()
            checks.check_real_run_gate(self.session)
            self.session.updated_at = self._now()
            return self.session
        probe = checks.check_real_safe_probe()
        self.session.artifacts["real_safe_probe"] = probe.as_dict()
        self._run_all()
        return self.session

    def run_stage(self, stage_id: str) -> CommissioningSession:
        for step in self.session.steps:
            if step.stage_id == stage_id:
                self._run_step(step)
        self.session.updated_at = self._now()
        return self.session

    def run_step(self, step_id: str) -> CommissioningSession:
        for step in self.session.steps:
            if step.step_id == step_id:
                self._run_step(step)
                break
        self.session.updated_at = self._now()
        return self.session

    def mark_manual_confirmed(self, step_id: str) -> None:
        for step in self.session.steps:
            if step.step_id == step_id:
                step.artifacts["manual_confirmed"] = True
                step.message = (step.message + " [manual confirmed]").strip()

    def block_step(self, step_id: str, reason: str) -> None:
        for step in self.session.steps:
            if step.step_id == step_id:
                step.status = "blocked"
                step.fail_reason = reason
                step.message = reason
                step.finished_at = self._now()
                append_failure_record(self.session, step, reason)

    def snapshot(self) -> dict[str, Any]:
        self.session.hardware_mode = get_hardware_mode().value
        self.session.real_hardware_enabled = is_real_hardware_enabled()
        return self.session.as_dict()

    def _run_all(self) -> None:
        for step in self.session.steps:
            self._run_step(step)
        self.session.updated_at = self._now()
