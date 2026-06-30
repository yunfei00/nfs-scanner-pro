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

_KNOWN_PROJECTS: dict[str, dict] = {p["name"]: deepcopy(p) for p in RECENT_PROJECTS}

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


def get_recent_project_names() -> list[str]:
    return [p["name"] for p in RECENT_PROJECTS]


def apply_workspace_state(current_project: dict, recent_names: list[str]) -> None:
    """从 workspace JSON 恢复项目 Mock 内存态。"""
    global CURRENT_PROJECT, RECENT_PROJECTS
    CURRENT_PROJECT = deepcopy(current_project)
    RECENT_PROJECTS = []
    for name in recent_names:
        entry = _resolve_project_entry(name)
        if entry is not None:
            RECENT_PROJECTS.append(deepcopy(entry))
    if CURRENT_PROJECT.get("name"):
        _register_known_project(CURRENT_PROJECT)


def _resolve_project_entry(name: str) -> dict | None:
    if not name:
        return None
    if name in _KNOWN_PROJECTS:
        return _KNOWN_PROJECTS[name]
    entry = _stub_project(name)
    _KNOWN_PROJECTS[name] = entry
    return entry


def _stub_project(name: str) -> dict:
    return {
        "name": name,
        "path": f"D:/NFS_Projects/{name}",
        "pcb": name,
        "default_region": "CPU_Area",
    }


def _register_known_project(project: dict) -> None:
    entry = {
        "name": project["name"],
        "path": project.get("path", f"D:/NFS_Projects/{project['name']}"),
        "pcb": project.get("pcb", project["name"]),
        "default_region": project.get("default_region", "CPU_Area"),
    }
    _KNOWN_PROJECTS[entry["name"]] = deepcopy(entry)


def create_project_mock(name: str, path: str, pcb: str, region: str) -> dict:
    project = {
        "name": name,
        "path": path,
        "pcb": pcb,
        "default_region": region,
        "status": "opened",
    }
    set_current_project(project)
    _register_known_project(project)
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
    return CURRENT_PROJECT.get("name") or CURRENT_PROJECT.get("pcb") or "未打开项目"


def get_scan_project_name() -> str:
    """扫描结果持久化使用的 Mock 项目名。"""
    project = get_current_project()
    if project.get("status") == "closed":
        return "Mock_Project"
    return project.get("name") or project.get("pcb") or "Mock_Project"


def _upsert_recent(project: dict) -> None:
    entry = {
        "name": project["name"],
        "path": project["path"],
        "pcb": project["pcb"],
        "default_region": project["default_region"],
    }
    global RECENT_PROJECTS
    RECENT_PROJECTS = [entry] + [p for p in RECENT_PROJECTS if p["name"] != entry["name"]]
    _KNOWN_PROJECTS[entry["name"]] = deepcopy(entry)
