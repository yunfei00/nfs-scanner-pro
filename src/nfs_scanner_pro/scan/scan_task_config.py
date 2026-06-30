"""扫描任务配置 — Release 019。"""

from __future__ import annotations

from dataclasses import dataclass, fields

from nfs_scanner_pro.ui import mock_data


@dataclass
class ScanTaskConfig:
    project_name: str = "iPhone16_Mainboard"
    region_name: str = "CPU_Area"
    probe_name: str = "Hx(100 μm)"
    frequency: str = "2.450 GHz"
    trace: str = "Trace 1"
    start_x: float = 10.00
    start_y: float = -150.00
    start_z: float = 5.00
    end_x: float = 190.00
    end_y: float = -10.00
    end_z: float = 5.00
    step_x: float = 2.00
    step_y: float = 2.00
    step_z: float = 0.00
    dwell_ms: int = 50
    average_count: int = 1
    speed_mm_min: int = 1000
    scan_mode: str = "蛇形扫描"
    total_points: int = 6461

    @classmethod
    def default(cls) -> ScanTaskConfig:
        return cls()

    @classmethod
    def from_mock_data(cls) -> ScanTaskConfig:
        start = mock_data.SCAN_START_POSITION
        end = mock_data.SCAN_END_POSITION
        step = mock_data.SCAN_STEP
        return cls(
            project_name=mock_data.PROJECT_NAME,
            region_name=mock_data.REGION_NAME,
            probe_name=mock_data.PROBE_NAME,
            frequency=mock_data.FREQUENCY,
            trace="Trace 1",
            start_x=start["x"],
            start_y=start["y"],
            start_z=start["z"],
            end_x=end["x"],
            end_y=end["y"],
            end_z=end["z"],
            step_x=step["x"],
            step_y=step["y"],
            step_z=step["z"],
            total_points=mock_data.SCAN_TOTAL_POINTS,
            speed_mm_min=mock_data.MOTION_STATE["speed"],
        )

    @classmethod
    def from_current_project(cls) -> ScanTaskConfig:
        from nfs_scanner_pro import project_mock

        project = project_mock.get_current_project()
        if project.get("status") == "closed":
            return cls.from_mock_data()
        start = mock_data.SCAN_START_POSITION
        end = mock_data.SCAN_END_POSITION
        step = mock_data.SCAN_STEP
        return cls(
            project_name=project.get("name") or mock_data.PROJECT_NAME,
            region_name=project.get("default_region") or mock_data.REGION_NAME,
            probe_name=mock_data.PROBE_NAME,
            frequency=mock_data.FREQUENCY,
            trace="Trace 1",
            start_x=start["x"],
            start_y=start["y"],
            start_z=start["z"],
            end_x=end["x"],
            end_y=end["y"],
            end_z=end["z"],
            step_x=step["x"],
            step_y=step["y"],
            step_z=step["z"],
            total_points=mock_data.SCAN_TOTAL_POINTS,
            speed_mm_min=mock_data.MOTION_STATE["speed"],
        )

    def as_dict(self) -> dict:
        return {field.name: getattr(self, field.name) for field in fields(self)}
