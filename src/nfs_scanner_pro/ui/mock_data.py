"""Release 010 Mock 数据 — 仅用于 UI 原型展示。"""

from __future__ import annotations

PROJECT_NAME = "iPhone16_Mainboard"
REGION_NAME = "CPU_Area"
PROBE_NAME = "Hx(100 μm)"
FREQUENCY = "2.450 GHz"
POINTS = 6461
GRID_X = 91
GRID_Y = 71

POSITION = {
    "x": 45.20,
    "y": -28.30,
    "z": 5.00,
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

BREADCRUMB = f"项目 > {REGION_NAME} > Hx Probe > {FREQUENCY} > {POINTS} pts"

STATUS_BAR = {
    "state": "准备就绪",
    "progress": "0%",
    "points": f"0 / {POINTS}",
    "remaining": "00:12:31",
    "date": "2025-06-16",
    "time": "14:31:10",
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
    "start": {"x": 0.0, "y": 0.0, "z": 5.0},
    "end": {"x": 90.0, "y": 70.0, "z": 5.0},
    "step": {"x": 1.0, "y": 1.0, "z": 0.0},
    "points_label": f"{GRID_X} x {GRID_Y} = {POINTS}",
    "area_mm2": "36000 mm²",
    "path_length": "16.20 m",
    "estimated_time": "00:32:18",
}
