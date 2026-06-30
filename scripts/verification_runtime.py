"""验收 runtime 隔离 — Release_031。"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent


def get_repo_root() -> Path:
    return _REPO_ROOT


def get_runtime_dir() -> Path:
    return get_repo_root() / "runtime"


def get_verification_runtime_dir() -> Path:
    path = get_runtime_dir() / "verification"
    path.mkdir(parents=True, exist_ok=True)
    return path


def normalize_release_id(release_id: str) -> str:
    text = str(release_id).strip().upper()
    if text.startswith("R"):
        return text
    digits = re.sub(r"\D", "", text)
    if not digits:
        raise ValueError(f"invalid release_id: {release_id!r}")
    return f"R{digits}"


def get_release_runtime_dir(release_id: str) -> Path:
    path = get_verification_runtime_dir() / normalize_release_id(release_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_release_runtime(release_id: str) -> None:
    """只清理 runtime/verification/Rxxx，不触碰 runtime/mock_projects。"""
    base = get_verification_runtime_dir()
    target = base / normalize_release_id(release_id)
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)


def clean_all_verification_runtime() -> None:
    base = get_verification_runtime_dir()
    if not base.is_dir():
        return
    for child in base.iterdir():
        if child.is_dir():
            shutil.rmtree(child)


def make_project_scan_dir(release_id: str, project_name: str, task_id: str) -> Path:
    safe_task = "".join(c if c.isalnum() or c in "-_." else "_" for c in task_id.strip())
    path = (
        get_release_runtime_dir(release_id)
        / "mock_projects"
        / project_name
        / "scans"
        / (safe_task or "ST-UNKNOWN")
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


def make_project_report_dir(release_id: str, project_name: str, report_id: str) -> Path:
    safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in report_id.strip())
    path = (
        get_release_runtime_dir(release_id)
        / "mock_projects"
        / project_name
        / "reports"
        / (safe_id or "RP-UNKNOWN")
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


def assert_runtime_ignored_by_git() -> tuple[bool, str]:
    """确认 runtime 与 verification 子目录被 .gitignore 覆盖。"""
    gitignore = get_repo_root() / ".gitignore"
    if not gitignore.is_file():
        return False, ".gitignore missing"
    text = gitignore.read_text(encoding="utf-8")
    if "runtime/" not in text:
        return False, "runtime/ not in .gitignore"
    samples = (
        get_runtime_dir() / "workspace_state_mock.json",
        get_verification_runtime_dir() / "R031" / "mock_projects" / "Demo" / "scans" / "ST-1",
    )
    for sample in samples:
        rel = sample.relative_to(get_repo_root()).as_posix()
        if not rel.startswith("runtime/"):
            return False, f"unexpected path {rel}"
    return True, "ok"
