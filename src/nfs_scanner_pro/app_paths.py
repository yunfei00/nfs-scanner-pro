"""应用路径 — Mock 运行时目录（Release 017）。"""

from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def get_runtime_dir() -> Path:
    runtime = get_project_root() / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    return runtime


def get_workspace_state_path() -> Path:
    return get_runtime_dir() / "workspace_state_mock.json"


def _safe_dir_name(name: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in "-_." else "_" for c in name.strip())
    return cleaned or "Mock_Project"


def get_mock_projects_dir() -> Path:
    directory = get_runtime_dir() / "mock_projects"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_mock_project_dir(project_name: str) -> Path:
    directory = get_mock_projects_dir() / _safe_dir_name(project_name)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_mock_scan_dir(project_name: str, task_id: str) -> Path:
    directory = get_mock_project_dir(project_name) / "scans" / _safe_dir_name(task_id)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
