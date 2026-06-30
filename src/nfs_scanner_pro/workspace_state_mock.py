"""工作区状态 Mock 持久化 — JSON 文件，不接真实项目数据（Release 017）。"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from nfs_scanner_pro.app_paths import get_workspace_state_path

DEFAULT_WORKSPACE_STATE: dict[str, Any] = {
    "current_project": {
        "name": "iPhone16_Mainboard",
        "path": "D:/NFS_Projects/iPhone16_Mainboard",
        "pcb": "iPhone16_Mainboard",
        "default_region": "CPU_Area",
        "status": "opened",
    },
    "recent_projects": [
        "Demo_Project_001",
        "iPhone16_Mainboard",
        "RF_Module_Test",
    ],
    "last_page": "scan",
    "navigation_expanded": False,
    "right_dock_visible": True,
    "window": {
        "width": 1600,
        "height": 1000,
        "maximized": True,
    },
}

_PAGE_NAMES = frozenset({"scan", "device", "analysis", "report"})

_state: dict[str, Any] = deepcopy(DEFAULT_WORKSPACE_STATE)
_last_load_ok = True


def get_state() -> dict[str, Any]:
    return deepcopy(_state)


def load_workspace_state() -> tuple[dict[str, Any], bool]:
    """读取 JSON；失败时回退默认配置。返回 (state, ok)。"""
    global _state, _last_load_ok
    path = get_workspace_state_path()
    if not path.is_file():
        _state = deepcopy(DEFAULT_WORKSPACE_STATE)
        _last_load_ok = True
        return get_state(), True

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("workspace state root must be object")
        _state = _normalize_state(raw)
        _last_load_ok = True
        return get_state(), True
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"[WorkspaceMock] load failed: {exc}", flush=True)
        _state = deepcopy(DEFAULT_WORKSPACE_STATE)
        _last_load_ok = False
        return get_state(), False


def save_workspace_state(state: dict[str, Any] | None = None) -> None:
    global _state
    if state is not None:
        _state = _normalize_state(state)
    path = get_workspace_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def reset_workspace_state() -> dict[str, Any]:
    global _state, _last_load_ok
    _state = deepcopy(DEFAULT_WORKSPACE_STATE)
    _last_load_ok = True
    path = get_workspace_state_path()
    if path.is_file():
        path.unlink()
    save_workspace_state()
    return get_state()


def update_current_project(project: dict[str, Any]) -> None:
    _state["current_project"] = deepcopy(project)
    save_workspace_state()


def update_recent_projects(names: list[str]) -> None:
    _state["recent_projects"] = list(names)
    save_workspace_state()


def update_last_page(page_name: str) -> None:
    if page_name not in _PAGE_NAMES:
        return
    _state["last_page"] = page_name
    save_workspace_state()


def update_navigation_expanded(expanded: bool) -> None:
    _state["navigation_expanded"] = bool(expanded)
    save_workspace_state()


def update_right_dock_visible(visible: bool) -> None:
    _state["right_dock_visible"] = bool(visible)
    save_workspace_state()


def update_window_state(width: int, height: int, maximized: bool) -> None:
    _state["window"] = {
        "width": max(400, int(width)),
        "height": max(300, int(height)),
        "maximized": bool(maximized),
    }
    save_workspace_state()


def snapshot_from_runtime(
    *,
    current_project: dict[str, Any],
    recent_projects: list[str],
    last_page: str,
    navigation_expanded: bool,
    right_dock_visible: bool,
    width: int,
    height: int,
    maximized: bool,
) -> None:
    global _state
    _state = _normalize_state(
        {
            "current_project": current_project,
            "recent_projects": recent_projects,
            "last_page": last_page,
            "navigation_expanded": navigation_expanded,
            "right_dock_visible": right_dock_visible,
            "window": {
                "width": width,
                "height": height,
                "maximized": maximized,
            },
        }
    )
    save_workspace_state()


def page_index_to_name(page_index: int) -> str:
    return ("scan", "device", "analysis", "report")[page_index]


def page_name_to_index(page_name: str) -> int:
    mapping = {"scan": 0, "device": 1, "analysis": 2, "report": 3}
    return mapping.get(page_name, 0)


def _normalize_state(raw: dict[str, Any]) -> dict[str, Any]:
    state = deepcopy(DEFAULT_WORKSPACE_STATE)
    project = raw.get("current_project")
    if isinstance(project, dict):
        state["current_project"] = {
            "name": str(project.get("name", "")),
            "path": str(project.get("path", "")),
            "pcb": str(project.get("pcb", "")),
            "default_region": str(project.get("default_region", "CPU_Area")),
            "status": str(project.get("status", "opened")),
        }

    recent = raw.get("recent_projects")
    if isinstance(recent, list):
        state["recent_projects"] = [str(name) for name in recent if name]

    last_page = raw.get("last_page")
    if isinstance(last_page, str) and last_page in _PAGE_NAMES:
        state["last_page"] = last_page

    if "navigation_expanded" in raw:
        state["navigation_expanded"] = bool(raw["navigation_expanded"])

    if "right_dock_visible" in raw:
        state["right_dock_visible"] = bool(raw["right_dock_visible"])

    window = raw.get("window")
    if isinstance(window, dict):
        state["window"] = {
            "width": max(400, int(window.get("width", 1600))),
            "height": max(300, int(window.get("height", 1000))),
            "maximized": bool(window.get("maximized", True)),
        }

    return state
