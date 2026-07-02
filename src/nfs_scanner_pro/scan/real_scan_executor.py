"""真实扫描执行器骨架 — dry-run / fake-run / real-run（Release 044）。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from nfs_scanner_pro.devices.real.hardware_config import (
    SCAN_EXECUTION_DISABLED_MESSAGE,
    is_real_hardware_enabled,
    is_real_motion_move_enabled,
    is_real_scan_execution_enabled,
    is_real_spectrum_sweep_enabled,
    is_real_spectrum_trace_read_enabled,
)
from nfs_scanner_pro.devices.real.hardware_safety import require_real_scan_execution_enabled
from nfs_scanner_pro.devices.real.real_device_manager import RealDeviceManager
from nfs_scanner_pro.scan.real_scan_plan import SmallAreaScanPlan
from nfs_scanner_pro.scan.real_scan_result_writer import build_summary, save_scan_result
from nfs_scanner_pro.scan.real_scan_safety import validate_scan_plan
from nfs_scanner_pro.scan.real_scan_state import RealScanProgress, RealScanState


class RealScanExecutor:
    def __init__(self, manager: RealDeviceManager | None = None) -> None:
        self.manager = manager or RealDeviceManager()
        self.plan: SmallAreaScanPlan | None = None
        self.task_id = ""
        self.state = RealScanState.CREATED
        self.progress: RealScanProgress | None = None
        self._logs: list[dict[str, Any]] = []
        self._point_results: list[dict[str, Any]] = []
        self._stop_requested = False
        self._paused = False

    def load_plan(self, plan: SmallAreaScanPlan) -> dict[str, Any]:
        validation = validate_scan_plan(plan)
        self.plan = plan
        self.task_id = f"RS-{uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.state = RealScanState.READY if validation.get("ok") else RealScanState.FAILED
        self.progress = RealScanProgress(
            task_id=self.task_id,
            plan_id=plan.plan_id,
            total_points=plan.point_count(),
            current_index=-1,
            completed_points=0,
            failed_points=0,
            state=self.state.value,
            message=str(validation.get("summary", "")),
            started_at=now,
            updated_at=now,
        )
        return {"ok": validation.get("ok", False), "validation": validation, "task_id": self.task_id}

    def dry_run(self) -> dict[str, Any]:
        if self.plan is None:
            return {"ok": False, "error": "未加载扫描计划"}
        validation = validate_scan_plan(self.plan)
        self._stop_requested = False
        self._paused = False
        self.state = RealScanState.RUNNING
        total = self.plan.point_count()
        self._update_progress(
            current_index=-1,
            message="dry-run 校验中",
            completed=0,
            failed=0,
        )
        self._logs.append({"event": "dry_run_start", "total_points": total})
        self.state = RealScanState.COMPLETED if validation.get("ok") else RealScanState.FAILED
        self._update_progress(
            current_index=total - 1 if total else -1,
            message="dry-run 完成",
            completed=0,
            failed=0 if validation.get("ok") else total,
        )
        self._logs.append({"event": "dry_run_done", "validation": validation.get("summary", "")})
        summary = build_summary(
            task_id=self.task_id,
            plan_id=self.plan.plan_id,
            mode="dry_run",
            total_points=self.plan.point_count(),
            completed_points=0,
            failed_points=0,
            state=self.state.value,
        )
        paths = save_scan_result(
            self.task_id,
            plan_id=self.plan.plan_id,
            points=[],
            summary=summary,
            logs=self._logs,
        )
        return {"ok": validation.get("ok", False), "mode": "dry_run", "paths": paths, "summary": summary}

    def fake_run(self) -> dict[str, Any]:
        if self.plan is None:
            return {"ok": False, "error": "未加载扫描计划"}
        self._stop_requested = False
        self._paused = False
        self.manager.enable_fake_transports()
        self.manager.motion.connect()
        self.manager.spectrum.connect()
        self.state = RealScanState.RUNNING
        completed = 0
        failed = 0
        self._point_results = []
        self._logs = []

        for point in self.plan.points:
            if self._stop_requested:
                self.state = RealScanState.STOPPED
                break
            while self._paused:
                self.state = RealScanState.PAUSED
            self.state = RealScanState.RUNNING
            self._update_progress(
                current_index=point.index,
                message=f"fake 扫描点 {point.index}",
                completed=completed,
                failed=failed,
            )
            move = self.manager.motion.move_to(
                x=point.x,
                y=point.y,
                z=point.z,
                dry_run=False,
            )
            marker = self.manager.spectrum.read_marker_amplitude()
            if not marker.get("ok"):
                marker = {
                    "ok": True,
                    "frequency_hz": 2450000000.0,
                    "amplitude_dbm": -23.45,
                    "unit": "dBm",
                    "fake": True,
                }
            sample_ok = bool(move.get("ok")) and bool(marker.get("ok"))
            if sample_ok:
                completed += 1
            else:
                failed += 1
            now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            row = {
                "index": point.index,
                "x": point.x,
                "y": point.y,
                "z": point.z,
                "frequency_hz": marker.get("frequency_hz", 2450000000.0),
                "amplitude_dbm": marker.get("amplitude_dbm", -23.45),
                "unit": marker.get("unit", "dBm"),
                "motion_state": "Idle",
                "sample_ok": sample_ok,
                "error": "" if sample_ok else "fake sample failed",
                "timestamp_iso": now,
            }
            self._point_results.append(row)
            self._logs.append({"index": point.index, "move": move, "marker": marker})

        if self.state not in (RealScanState.STOPPED, RealScanState.FAILED):
            self.state = RealScanState.COMPLETED
        self._update_progress(
            message="fake-run 完成",
            completed=completed,
            failed=failed,
            current_index=self.plan.point_count() - 1,
        )
        summary = build_summary(
            task_id=self.task_id,
            plan_id=self.plan.plan_id,
            mode="fake_run",
            total_points=self.plan.point_count(),
            completed_points=completed,
            failed_points=failed,
            state=self.state.value,
        )
        paths = save_scan_result(
            self.task_id,
            plan_id=self.plan.plan_id,
            points=self._point_results,
            summary=summary,
            logs=self._logs,
        )
        self.manager.disconnect_all()
        return {
            "ok": completed > 0,
            "mode": "fake_run",
            "completed_points": completed,
            "paths": paths,
            "summary": summary,
        }

    def real_run(self) -> dict[str, Any]:
        from nfs_scanner_pro.devices.hardware_mode import is_real_mode

        if not is_real_mode():
            return {
                "ok": False,
                "blocked": True,
                "error": "NFS_HARDWARE_MODE 必须为 real",
            }
        if not is_real_hardware_enabled():
            return {"ok": False, "blocked": True, "error": "NFS_ENABLE_REAL_HARDWARE 未启用"}
        ok_exec, message = require_real_scan_execution_enabled()
        if not ok_exec:
            return {"ok": False, "blocked": True, "error": message}
        if not is_real_motion_move_enabled():
            return {"ok": False, "blocked": True, "error": "NFS_ENABLE_REAL_MOTION_MOVE 未启用"}
        if not (
            is_real_spectrum_trace_read_enabled() or is_real_spectrum_sweep_enabled()
        ):
            return {
                "ok": False,
                "blocked": True,
                "error": "需要 NFS_ENABLE_REAL_SPECTRUM_TRACE_READ 或 NFS_ENABLE_REAL_SPECTRUM_SWEEP",
            }
        return {
            "ok": False,
            "blocked": True,
            "error": SCAN_EXECUTION_DISABLED_MESSAGE,
            "message": "real-run 入口已实现，但默认 blocked；请逐项开启安全开关后再现场调试",
        }

    def pause(self) -> dict[str, Any]:
        self._paused = True
        self.state = RealScanState.PAUSED
        return {"ok": True, "state": self.state.value}

    def resume(self) -> dict[str, Any]:
        self._paused = False
        self.state = RealScanState.RUNNING
        return {"ok": True, "state": self.state.value}

    def stop(self) -> dict[str, Any]:
        self._stop_requested = True
        self._paused = False
        self.state = RealScanState.STOPPING
        self._logs.append({"event": "stop_requested", "real_device_stop": False})
        if self.progress is not None:
            self.progress.message = "停止请求已记录（不发送真实 stop）"
            self.progress.state = self.state.value
        return {"ok": True, "state": self.state.value}

    def snapshot(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "state": self.state.value,
            "progress": self.progress.as_dict() if self.progress else None,
            "point_results": list(self._point_results),
        }

    def _update_progress(
        self,
        *,
        message: str,
        completed: int,
        failed: int,
        current_index: int | None = None,
    ) -> None:
        if self.progress is None or self.plan is None:
            return
        if current_index is not None:
            self.progress.current_index = current_index
        self.progress.completed_points = completed
        self.progress.failed_points = failed
        self.progress.state = self.state.value
        self.progress.message = message
        self.progress.updated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
