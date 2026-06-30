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
