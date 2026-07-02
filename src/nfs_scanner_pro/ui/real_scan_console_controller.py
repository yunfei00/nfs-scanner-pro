"""真实扫描控制台控制器 — Release 046。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from nfs_scanner_pro.devices.hardware_mode import get_hardware_mode, is_real_mode
from nfs_scanner_pro.devices.real.hardware_config import (
    is_real_hardware_enabled,
    is_real_scan_execution_enabled,
)
from nfs_scanner_pro.scan.real_scan_executor import RealScanExecutor
from nfs_scanner_pro.scan.real_scan_plan import SmallAreaScanPlan, generate_3x3_scan_plan
from nfs_scanner_pro.scan.real_scan_plan_persistence import (
    build_summary as build_plan_summary,
    load_scan_plan,
    save_scan_plan,
)
from nfs_scanner_pro.scan.real_scan_safety import validate_scan_plan
from nfs_scanner_pro.ui.real_scan_console_model import RealScanConsoleModel


REAL_RUN_SAFE_MESSAGE = (
    "Real Run 未启用。\n"
    "需要同时设置：\n"
    "NFS_HARDWARE_MODE=real\n"
    "NFS_ENABLE_REAL_HARDWARE=1\n"
    "NFS_ENABLE_REAL_SCAN_EXECUTION=1"
)


def _plan_ranges(plan: SmallAreaScanPlan) -> dict[str, Any]:
    xs = [point.x for point in plan.points]
    ys = [point.y for point in plan.points]
    zs = [point.z for point in plan.points]
    return {
        "x_range": [min(xs), max(xs)] if xs else [0.0, 0.0],
        "y_range": [min(ys), max(ys)] if ys else [0.0, 0.0],
        "z_range": [min(zs), max(zs)] if zs else [0.0, 0.0],
    }


def _plan_summary_dict(plan: SmallAreaScanPlan, validation: dict[str, Any]) -> dict[str, Any]:
    ranges = _plan_ranges(plan)
    return {
        "plan_id": plan.plan_id,
        "project_name": plan.project_name,
        "region_name": plan.region_name,
        "point_count": plan.point_count(),
        "x_range": ranges["x_range"],
        "y_range": ranges["y_range"],
        "z_range": ranges["z_range"],
        "frequency": plan.frequency,
        "trace": plan.trace,
        "dry_run": plan.dry_run,
        "safe_mode": plan.safe_mode,
        "valid": validation.get("valid", validation.get("ok", False)),
        "validation_summary": validation.get("summary", ""),
    }


class RealScanConsoleController:
    def __init__(self) -> None:
        self.model = RealScanConsoleModel()
        self._executor: RealScanExecutor | None = None
        self._plan: SmallAreaScanPlan | None = None
        self.refresh_hardware_mode()

    def refresh_hardware_mode(self) -> None:
        self.model.hardware_mode = get_hardware_mode().value
        enabled, message = self._real_run_gate()
        self.model.real_run_enabled = enabled
        self.model.safe_message = "" if enabled else message

    def _real_run_gate(self) -> tuple[bool, str]:
        if not is_real_mode():
            return False, REAL_RUN_SAFE_MESSAGE
        if not is_real_hardware_enabled():
            return False, REAL_RUN_SAFE_MESSAGE
        if not is_real_scan_execution_enabled():
            return False, REAL_RUN_SAFE_MESSAGE
        return True, ""

    def _ensure_executor(self) -> RealScanExecutor:
        if self._executor is None:
            self._executor = RealScanExecutor()
        return self._executor

    def load_plan(self, path: str | Path) -> dict[str, Any]:
        loaded = load_scan_plan(path)
        if not loaded.get("ok"):
            message = str(loaded.get("error", "加载计划失败"))
            self.model.append_log(message)
            return {"ok": False, "error": message}
        plan: SmallAreaScanPlan = loaded["plan"]
        validation = validate_scan_plan(plan)
        self._plan = plan
        executor = self._ensure_executor()
        executor.load_plan(plan)
        json_path = str(loaded.get("json_path", path))
        summary = _plan_summary_dict(plan, validation)
        self.model.set_plan(summary, json_path)
        self.model.append_log(f"已加载扫描计划：{json_path}")
        self.model.append_log(f"plan_id={plan.plan_id} point_count={plan.point_count()}")
        return {"ok": True, "plan": plan, "validation": validation, "summary": summary}

    def load_default_3x3_plan(self) -> dict[str, Any]:
        plan = generate_3x3_scan_plan()
        validation = validate_scan_plan(plan)
        paths = save_scan_plan(plan, validation)
        self._plan = plan
        executor = self._ensure_executor()
        executor.load_plan(plan)
        json_path = str(paths["json_path"])
        summary = _plan_summary_dict(plan, validation)
        self.model.set_plan(summary, json_path)
        self.model.append_log("已加载默认 3x3 扫描计划")
        self.model.append_log(f"plan_id={plan.plan_id} point_count={plan.point_count()}")
        return {
            "ok": True,
            "plan": plan,
            "validation": validation,
            "paths": {k: str(v) for k, v in paths.items()},
            "summary": summary,
        }

    def validate_current_plan(self) -> dict[str, Any]:
        if self._plan is None:
            message = "未加载扫描计划"
            self.model.append_log(message)
            return {"ok": False, "error": message}
        validation = validate_scan_plan(self._plan)
        summary = build_plan_summary(self._plan, validation)
        self.model.set_plan(_plan_summary_dict(self._plan, validation), self.model.plan_path)
        self.model.append_log(f"计划校验：{validation.get('summary', validation)}")
        return {"ok": validation.get("ok", False), "validation": validation, "summary": summary}

    def run_dry_run(self) -> dict[str, Any]:
        if self._plan is None:
            return {"ok": False, "error": "未加载扫描计划"}
        executor = self._ensure_executor()
        if executor.plan is None:
            executor.load_plan(self._plan)
        self.model.execution_mode = "dry_run"
        self.model.append_log("开始 dry-run …")
        result = executor.dry_run()
        self._apply_executor_result(result)
        self.model.append_log(f"dry-run 完成：ok={result.get('ok')}")
        return result

    def run_fake_run(self) -> dict[str, Any]:
        if self._plan is None:
            return {"ok": False, "error": "未加载扫描计划"}
        executor = self._ensure_executor()
        executor._stop_requested = False
        executor._paused = False
        if executor.plan is None:
            executor.load_plan(self._plan)
        self.model.execution_mode = "fake_run"
        self.model.append_log("开始 fake-run（FakeTransport，不连接真实设备）…")
        result = executor.fake_run()
        self._apply_executor_result(result)
        self.model.append_log(
            f"fake-run 完成：completed={result.get('completed_points', 0)}"
        )
        return result

    def run_real_run(self) -> dict[str, Any]:
        self.refresh_hardware_mode()
        if not self.model.real_run_enabled:
            message = self.model.safe_message or REAL_RUN_SAFE_MESSAGE
            self.model.append_log(f"real-run blocked：{message.replace(chr(10), ' ')}")
            return {"ok": False, "blocked": True, "error": message}
        if self._plan is None:
            return {"ok": False, "blocked": True, "error": "未加载扫描计划"}
        executor = self._ensure_executor()
        if executor.plan is None:
            executor.load_plan(self._plan)
        self.model.execution_mode = "real_run"
        self.model.append_log("请求 real-run …")
        result = executor.real_run()
        if result.get("blocked"):
            self.model.append_log(f"real-run blocked：{result.get('error', '')}")
        else:
            self._apply_executor_result(result)
        return result

    def pause(self) -> dict[str, Any]:
        executor = self._ensure_executor()
        result = executor.pause()
        self.model.scan_state = result.get("state", "paused")
        self.model.append_log("已暂停")
        if executor.progress:
            self.model.set_progress(executor.progress.as_dict())
        return result

    def resume(self) -> dict[str, Any]:
        executor = self._ensure_executor()
        result = executor.resume()
        self.model.scan_state = result.get("state", "running")
        self.model.append_log("已恢复")
        if executor.progress:
            self.model.set_progress(executor.progress.as_dict())
        return result

    def stop(self) -> dict[str, Any]:
        executor = self._ensure_executor()
        result = executor.stop()
        self.model.scan_state = result.get("state", "stopping")
        self.model.append_log("已请求停止（不发送真实设备 stop 命令）")
        if executor.progress:
            self.model.set_progress(executor.progress.as_dict())
        return result

    def snapshot(self) -> dict[str, Any]:
        data = self.model.as_dict()
        if self._executor is not None:
            data["executor"] = self._executor.snapshot()
        return data

    def _apply_executor_result(self, result: dict[str, Any]) -> None:
        paths = result.get("paths") or {}
        if paths:
            self.model.set_outputs({key: str(value) for key, value in paths.items()})
            for key, value in paths.items():
                self.model.append_log(f"输出 {key}: {value}")
        summary = result.get("summary")
        if isinstance(summary, dict):
            self.model.append_log(
                f"summary completed={summary.get('completed_points')} "
                f"failed={summary.get('failed_points')}"
            )
        executor = self._executor
        if executor is not None and executor.progress is not None:
            self.model.set_progress(executor.progress.as_dict())
