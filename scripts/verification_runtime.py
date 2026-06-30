"""验收 runtime 隔离 — Release_031 / 032。"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_ENV_RUNTIME = "NFS_SCANNER_RUNTIME_DIR"
_ENV_RELEASE = "NFS_VERIFY_RELEASE_ID"


def get_repo_root() -> Path:
    return _REPO_ROOT


def get_default_runtime_dir() -> Path:
    path = get_repo_root() / "runtime"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_runtime_dir() -> Path:
    """仓库默认 runtime/（非隔离 override）。"""
    return get_default_runtime_dir()


def get_shared_mock_projects_dir() -> Path:
    return get_default_runtime_dir() / "mock_projects"


def release_id_to_dir_name(release_id: str) -> str:
    return normalize_release_id(release_id)


def normalize_release_id(release_id: str) -> str:
    text = str(release_id).strip().upper()
    if text.startswith("R"):
        return text
    digits = re.sub(r"\D", "", text)
    if not digits:
        raise ValueError(f"invalid release_id: {release_id!r}")
    return f"R{digits.zfill(3)}" if len(digits) <= 3 else f"R{digits}"


def get_verification_runtime_dir() -> Path:
    path = get_default_runtime_dir() / "verification"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_release_runtime_dir(release_id: str) -> Path:
    path = get_verification_runtime_dir() / release_id_to_dir_name(release_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_release_runtime(release_id: str) -> None:
    """只清理 runtime/verification/Rxxx，不触碰 runtime/mock_projects。"""
    base = get_verification_runtime_dir()
    target = base / release_id_to_dir_name(release_id)
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


def build_release_env(release_id: str, *, base_env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base_env or os.environ)
    runtime_dir = get_release_runtime_dir(release_id)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env["NFS_VERIFY_RELEASE_ID"] = release_id_to_dir_name(release_id)
    env["NFS_SCANNER_RUNTIME_DIR"] = str(runtime_dir.resolve())
    return env


def enter_release_runtime(release_id: str) -> Path:
    runtime_dir = get_release_runtime_dir(release_id)
    os.environ[_ENV_RUNTIME] = str(runtime_dir.resolve())
    os.environ[_ENV_RELEASE] = release_id_to_dir_name(release_id)
    return runtime_dir


def get_current_release_runtime() -> Path | None:
    override = os.environ.get(_ENV_RUNTIME)
    if not override:
        return None
    return Path(override)


def runtime_display_path(release_id: str) -> str:
    path = get_release_runtime_dir(release_id)
    try:
        return path.relative_to(get_repo_root()).as_posix()
    except ValueError:
        return str(path)


def list_release_runtime_files(release_id: str) -> list[Path]:
    root = get_release_runtime_dir(release_id)
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file())


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
    required = ("runtime/", "runtime/**/*.json", "runtime/**/*.csv")
    missing = [rule for rule in required if rule not in text]
    if missing:
        return False, f"missing rules: {', '.join(missing)}"
    samples = (
        get_default_runtime_dir() / "workspace_state_mock.json",
        get_verification_runtime_dir() / "R032" / "mock_projects" / "Demo" / "scans" / "ST-1",
    )
    for sample in samples:
        rel = sample.relative_to(get_repo_root()).as_posix()
        if not rel.startswith("runtime/"):
            return False, f"unexpected path {rel}"
    return True, "ok"
