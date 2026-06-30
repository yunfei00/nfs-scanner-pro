"""Release 011/012 Mock 数据 — 仅用于 UI 原型展示。"""

from __future__ import annotations

from nfs_scanner_pro import project_mock

PROJECT_NAME = "iPhone16_Mainboard"
REGION_NAME = "CPU_Area"
PROBE_NAME = "Hx(100 μm)"
FREQUENCY = "2.450 GHz"
POINTS = 6461
GRID_X = 91
GRID_Y = 71
SCAN_TASK = "ST-001"

SCAN_TOTAL_POINTS = 6461
SCAN_DEFAULT_REMAINING = "00:12:31"
SCAN_START_POSITION = {
    "x": 10.00,
    "y": -150.00,
    "z": 5.00,
}
SCAN_END_POSITION = {
    "x": 190.00,
    "y": -10.00,
    "z": 5.00,
}
SCAN_STEP = {
    "x": 2.00,
    "y": 2.00,
    "z": 0.00,
}

DEVICE_PROFILE = {
    "name": "Lab_Default_v1",
    "motion": "COM6 · 115200",
    "spectrum": "ZNA67 · TCP/IP",
    "camera": "USB3.0 Camera",
    "servo": "HxHy_Default",
}

MOTION_STATE = {
    "port": "COM6",
    "baudrate": 115200,
    "status": "已连接",
    "x": 45.20,
    "y": -28.30,
    "z": 5.00,
    "speed": 1000,
    "travel_x": "0 ~ 200",
    "travel_y": "0 ~ -300",
    "travel_z": "0 ~ 10",
}

SPECTRUM_STATE = {
    "model": "ZNA67",
    "connection": "TCP/IP",
    "address": "192.168.1.100:5025",
    "trace": "Trace 1",
    "freq_range": "1 MHz — 67 GHz",
    "current_freq": "2.450 GHz",
}

CAMERA_STATE = {
    "interface": "USB3.0",
    "resolution": "4096 × 3000",
    "status": "预览就绪",
    "capture_x": 0.0,
    "capture_y": 0.0,
    "capture_z": 5.00,
}

SERVO_STATE = {
    "current_probe": "Hx",
    "hy_status": "待命",
    "angle": "0.0°",
    "offset": "X +0.02 / Y -0.01 mm",
    "calibration": "已校准",
}

DEVICE_POLICY = {
    "auto_connect": True,
    "camera_optional": True,
    "block_scan_on_fault": True,
}

DEVICE_SAFETY = {
    "x_range": "0 ~ 200 mm",
    "y_range": "0 ~ -300 mm",
    "z_range": "0 ~ 10 mm",
    "default_speed": "1000 mm/min",
}

POSITION = {
    "x": MOTION_STATE["x"],
    "y": MOTION_STATE["y"],
    "z": MOTION_STATE["z"],
    "amp": -23.45,
}

DEVICE_STATUS = [
    {"name": "运动平台", "detail": "COM6", "status": "connected"},
    {"name": "频谱仪", "detail": "ZNA67", "status": "connected"},
    {"name": "相机", "detail": "USB3.0", "status": "connected"},
    {"name": "舵机系统", "detail": "", "status": "connected"},
]

DEVICE_TOOLTIPS = {
    "运动平台": (
        "运动平台\n"
        "端口：COM6\n"
        "波特率：115200\n"
        "状态：已连接\n"
        "坐标：X 45.20 / Y -28.30 / Z 5.00"
    ),
    "频谱仪": "频谱仪\n型号：ZNA67\n状态：已连接",
    "相机": "相机\n接口：USB3.0\n状态：已连接",
    "舵机系统": "舵机系统\n状态：已连接",
}

BREADCRUMB_SCAN = f"项目 > {REGION_NAME} > Hx 探头 > {FREQUENCY} > {POINTS} 点"
BREADCRUMB_ANALYSIS = (
    f"项目 > {REGION_NAME} > ScanTask {SCAN_TASK} > Trace 1 > {FREQUENCY}"
)


def apply_project(project: dict | None = None) -> None:
    """从 project_mock 同步全局 Mock 名称与 Breadcrumb 字符串。"""
    global PROJECT_NAME, REGION_NAME, BREADCRUMB_SCAN, BREADCRUMB_ANALYSIS
    if project is None:
        project = project_mock.get_current_project()
    if project.get("status") == "closed":
        PROJECT_NAME = "未打开项目"
    else:
        PROJECT_NAME = project.get("pcb") or project.get("name") or "未打开项目"
    if project.get("default_region"):
        REGION_NAME = project["default_region"]
    BREADCRUMB_SCAN = get_breadcrumb_scan()
    BREADCRUMB_ANALYSIS = get_breadcrumb_analysis()


def get_breadcrumb_scan() -> str:
    label = project_mock.project_display_name()
    return f"{label} > {REGION_NAME} > Hx 探头 > {FREQUENCY} > {POINTS} 点"


def get_breadcrumb_analysis() -> str:
    label = project_mock.project_display_name()
    return f"{label} > {REGION_NAME} > ScanTask {SCAN_TASK} > Trace 1 > {FREQUENCY}"


def get_breadcrumb_report(report_name: str) -> str:
    label = project_mock.project_display_name()
    return f"报告 > {label} > {report_name}"


# 启动时与 project_mock 默认项目对齐
apply_project()

ANALYSIS_TASK = {
    "scan_task": SCAN_TASK,
    "trace": "Trace 1",
    "frequency": FREQUENCY,
    "points": POINTS,
    "probe": PROBE_NAME,
    "mode": "幅度",
    "lut": "Turbo",
    "vmin": -90,
    "vmax": -10,
    "opacity": 72,
}

ANALYSIS_CURSOR = {
    "x": 45.20,
    "y": -28.30,
    "z": 5.00,
    "frequency": FREQUENCY,
    "amp": -23.45,
    "phase": 112.3,
}

ANALYSIS_FREQUENCIES = [
    "1.000 GHz",
    "2.450 GHz",
    "3.500 GHz",
    "6.000 GHz",
]

ANALYSIS_TRACES = [
    "Trace 1",
    "Trace 2",
]

DATE = "2025-06-16"
TIME = "14:31:10"

STATUS_SCAN = {
    "state": "准备就绪",
    "progress": 0,
    "extra1": f"扫描点：0 / {POINTS}",
    "extra2": "预计剩余时间：00:12:31",
}

STATUS_DEVICE = {
    "state": "设备就绪",
    "extra1": "已连接设备：4 / 4",
    "extra2": f"当前配置：{DEVICE_PROFILE['name']}",
}

STATUS_ANALYSIS = {
    "state": "分析就绪",
    "extra1": "Heatmap：已加载",
    "extra2": f"ScanTask：{SCAN_TASK} · {POINTS} pts",
}

STATUS_REPORT = {
    "state": "报告就绪",
    "extra1": "当前：CPU_Area_Hx_2.45GHz_报告",
    "extra2": "",
}

SCAN_SETTINGS = {
    "mode": "蛇形扫描",
    "dwell_ms": 50,
    "averages": 1,
    "speed_mm_min": 1000,
    "return_home": False,
    "live_heatmap": True,
}

REGION_SETTINGS = {
    "start": SCAN_START_POSITION,
    "end": SCAN_END_POSITION,
    "step": SCAN_STEP,
    "points_label": f"{GRID_X} × {GRID_Y} = {POINTS}",
    "area_mm2": "36000 mm²",
    "path_length": "16.20 m",
    "estimated_time": "00:32:18",
}

REPORTS = [
    {
        "id": "r1",
        "name": "CPU_Area_Hx_2.45GHz_报告",
        "title": "CPU_Area_Hx_2.45GHz_报告",
        "time": "2025-06-16 14:20",
        "meta": "2025-06-16 14:20 · Hx",
        "probe": "Hx",
        "project": "iPhone16_Mainboard",
        "region": "CPU_Area",
        "frequency": "2.450 GHz",
        "scan_time": "2025-06-16 14:20:33",
        "summary": (
            "CPU 区域在 2.450 GHz 出现局部辐射峰值（-23.45 dBm），"
            "位于 U2-CPU 封装右侧约 12 mm 处。建议进一步 Hx / Hy 对比分析。"
        ),
    },
    {
        "id": "r2",
        "name": "CPU_Area_Hy_2.45GHz_报告",
        "title": "CPU_Area_Hy_2.45GHz_报告",
        "time": "2025-06-15 09:45",
        "meta": "2025-06-15 09:45 · Hy",
        "probe": "Hy",
        "project": "iPhone16_Mainboard",
        "region": "CPU_Area",
        "frequency": "2.450 GHz",
        "scan_time": "2025-06-15 09:45:12",
        "summary": (
            "Hy 方向扫描显示 CPU 区域存在次级峰值，建议与 Hx 扫描结果叠加对比。"
        ),
    },
    {
        "id": "r3",
        "name": "全板初扫摘要",
        "title": "全板初扫_摘要",
        "time": "2025-06-10 16:30",
        "meta": "2025-06-10 16:30 · Hx",
        "probe": "Hx",
        "project": "iPhone16_Mainboard",
        "region": "FullBoard",
        "frequency": "2.450 GHz",
        "scan_time": "2025-06-10 16:30:00",
        "summary": (
            "全板初扫显示 CPU 区域、射频模块附近存在明显热点，建议进入局部精扫。"
        ),
    },
]

REPORT_SETTINGS = {
    "template": "标准 EMC 报告",
    "logo": "公司默认",
    "pdf_quality": "印刷（300 DPI）",
    "formats": ["PDF", "Word", "Excel"],
    "include_heatmap": True,
    "include_device_info": True,
    "include_scan_params": True,
    "include_raw_data": False,
    "include_summary": True,
}
