"""统一验收报告格式 — Release_031。"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass


@dataclass
class _CheckEntry:
    name: str
    ok: bool
    detail: str = ""
    elapsed_s: float | None = None
    skipped: bool = False


class VerificationReport:
    def __init__(self, release_id: str, title: str | None = None) -> None:
        self.release_id = release_id
        self.title = title or f"Release_{release_id} Verification"
        self._entries: list[_CheckEntry] = []
        self._started = time.perf_counter()
        self._timers: dict[str, float] = {}

    def start_check(self, name: str) -> None:
        self._timers[name] = time.perf_counter()

    def pass_check(self, name: str, detail: str = "", *, elapsed_s: float | None = None) -> None:
        elapsed = elapsed_s if elapsed_s is not None else self._pop_elapsed(name)
        self._entries.append(_CheckEntry(name=name, ok=True, detail=detail, elapsed_s=elapsed))

    def fail_check(self, name: str, detail: str = "", *, elapsed_s: float | None = None) -> None:
        elapsed = elapsed_s if elapsed_s is not None else self._pop_elapsed(name)
        self._entries.append(_CheckEntry(name=name, ok=False, detail=detail, elapsed_s=elapsed))

    def skip_check(self, name: str, detail: str = "") -> None:
        self._entries.append(_CheckEntry(name=name, ok=True, detail=detail, skipped=True))

    def _pop_elapsed(self, name: str) -> float | None:
        start = self._timers.pop(name, None)
        if start is None:
            return None
        return time.perf_counter() - start

    @property
    def entries(self) -> list[tuple[str, bool, str, float | None, bool]]:
        return [
            (e.name, e.ok, e.detail, e.elapsed_s, e.skipped)
            for e in self._entries
        ]

    def is_pass(self) -> bool:
        return all(e.ok for e in self._entries if not e.skipped)

    def exit_code(self) -> int:
        return 0 if self.is_pass() else 1

    @property
    def total_elapsed_s(self) -> float:
        return time.perf_counter() - self._started

    def _safe(self, text: str) -> str:
        encoding = sys.stdout.encoding or "utf-8"
        return text.encode(encoding, errors="backslashreplace").decode(
            encoding,
            errors="backslashreplace",
        )

    def render(self) -> str:
        lines = [f"{self.title}", ""]
        for entry in self._entries:
            if entry.skipped:
                status = "SKIP"
            else:
                status = "PASS" if entry.ok else "FAIL"
            line = f"[{status}] {entry.name}"
            if entry.elapsed_s is not None:
                line += f" {entry.elapsed_s:.2f}s"
            if entry.detail:
                line += f" — {entry.detail}"
            lines.append(self._safe(line))
        lines.append("")
        lines.append(f"RESULT: {'PASS' if self.is_pass() else 'FAIL'}")
        lines.append(f"TOTAL: {self.total_elapsed_s:.2f}s")
        if not self.is_pass():
            lines.append("")
            lines.append("Failures:")
            for entry in self._entries:
                if not entry.ok and not entry.skipped:
                    lines.append(f"  - {entry.name}: {entry.detail or 'failed'}")
        return "\n".join(lines)

    def print_report(self) -> None:
        print(self.render())
