"""统一命令结果 — Release 044。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class CommandResult:
    ok: bool
    action: str = ""
    enabled: bool = False
    blocked: bool = False
    dry_run: bool = False
    fake: bool = False
    message: str = ""
    data: dict[str, Any] | None = None
    error: str = ""
    raw: str = ""
    timestamp_iso: str = ""

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.data is None:
            payload["data"] = {}
        return payload


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def success(
    action: str,
    *,
    message: str = "",
    data: dict[str, Any] | None = None,
    raw: str = "",
    enabled: bool = True,
    fake: bool = False,
    dry_run: bool = False,
) -> CommandResult:
    return CommandResult(
        ok=True,
        action=action,
        enabled=enabled,
        blocked=False,
        dry_run=dry_run,
        fake=fake,
        message=message,
        data=data or {},
        raw=raw,
        timestamp_iso=_now_iso(),
    )


def fail(action: str, error: str, *, data: dict[str, Any] | None = None) -> CommandResult:
    return CommandResult(
        ok=False,
        action=action,
        error=error,
        message=error,
        data=data or {},
        timestamp_iso=_now_iso(),
    )


def blocked(action: str, message: str, *, data: dict[str, Any] | None = None) -> CommandResult:
    return CommandResult(
        ok=False,
        action=action,
        blocked=True,
        message=message,
        error=message,
        data=data or {},
        timestamp_iso=_now_iso(),
    )


def disabled(action: str, message: str) -> CommandResult:
    return CommandResult(
        ok=False,
        action=action,
        enabled=False,
        blocked=True,
        message=message,
        error=message,
        timestamp_iso=_now_iso(),
    )


def dry_run_result(
    action: str,
    *,
    message: str = "",
    data: dict[str, Any] | None = None,
    raw: str = "",
    fake: bool = False,
) -> CommandResult:
    return CommandResult(
        ok=True,
        action=action,
        dry_run=True,
        fake=fake,
        message=message or "dry-run：未发送命令",
        data=data or {},
        raw=raw,
        timestamp_iso=_now_iso(),
    )
