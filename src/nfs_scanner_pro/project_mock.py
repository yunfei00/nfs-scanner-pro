"""项目文件夹 Mock — 内存态，不写真实文件（Release 016）。"""

from __future__ import annotations

from copy import deepcopy

CURRENT_PROJECT: dict = {
    "name": "iPhone16_Mainboard",
    "path": "D:/NFS_Projects/iPhone16_Mainboard",
    "pcb": "iPhone16_Mainboard",
    "default_region": "CPU_Area",
    "status": "opened",
}

RECENT_PROJECTS: list[dict] = [
    {
        "name": "Demo_Project_001",
        "path": "D:/NFS_Projects/Demo_Project_001",
        "pcb": "Demo_Board",
        "default_region": "CPU_Area",
    },
    {
        "name": "iPhone16_Mainboard",
        "path": "D:/NFS_Projects/iPhone16_Mainboard",
        "pcb": "iPhone16_Mainboard",
        "default_region": "CPU_Area",
    },
    {
        "name": "RF_Module_Test",
        "path": "D:/NFS_Projects/RF_Module_Test",
        "pcb": "RF_Module",
        "default_region": "RF_Area",
    },
]

_CLOSED_PROJECT: dict = {
    "name": "",
    "path": "",
    "pcb": "",
    "default_region": "",
    "status": "closed",
}


def get_current_project() -> dict:
    return deepcopy(CURRENT_PROJECT)


def set_current_project(project: dict) -> dict:
    global CURRENT_PROJECT
    CURRENT_PROJECT = deepcopy(project)
    CURRENT_PROJECT["status"] = "opened"
    return get_current_project()


def get_recent_projects() -> list[dict]:
    return deepcopy(RECENT_PROJECTS)


def create_project_mock(name: str, path: str, pcb: str, region: str) -> dict:
    project = {
        "name": name,
        "path": path,
        "pcb": pcb,
        "default_region": region,
        "status": "opened",
    }
    set_current_project(project)
    _upsert_recent(project)
    return get_current_project()


def open_project_mock(project_name: str) -> dict:
    for item in RECENT_PROJECTS:
        if item["name"] == project_name or item["pcb"] == project_name:
            return set_current_project({**item, "status": "opened"})
    return get_current_project()


def save_project_mock() -> dict:
    return get_current_project()


def close_project_mock() -> dict:
    global CURRENT_PROJECT
    CURRENT_PROJECT = deepcopy(_CLOSED_PROJECT)
    return get_current_project()


def project_display_name() -> str:
    if CURRENT_PROJECT.get("status") == "closed":
        return "未打开项目"
    return CURRENT_PROJECT.get("pcb") or CURRENT_PROJECT.get("name") or "未打开项目"


def _upsert_recent(project: dict) -> None:
    entry = {
        "name": project["name"],
        "path": project["path"],
        "pcb": project["pcb"],
        "default_region": project["default_region"],
    }
    global RECENT_PROJECTS
    RECENT_PROJECTS = [entry] + [p for p in RECENT_PROJECTS if p["name"] != entry["name"]]
