#!/usr/bin/env python3
"""
校验 spec/Registry/*.yaml 中引用的 Markdown 路径是否存在。

用途：Release 009.9 AI Knowledge Index 维护；防止 Registry 死链。
依赖：仅 Python 标准库。不影响业务代码。

用法（仓库根目录）：
    python scripts/check_spec_registry_paths.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_DIR = REPO_ROOT / "spec" / "Registry"

# 匹配 yaml 中以 docs/ 或 spec/ 开头的 .md 路径（允许引号包裹）
MD_PATH_PATTERN = re.compile(
    r"""['"]?((?:docs|spec)/[^\s#'"]+\.md)['"]?"""
)


def collect_yaml_files() -> list[Path]:
    if not REGISTRY_DIR.is_dir():
        print(f"Registry directory not found: {REGISTRY_DIR}", file=sys.stderr)
        sys.exit(2)
    return sorted(REGISTRY_DIR.glob("*.yaml"))


def extract_md_paths(yaml_path: Path) -> set[str]:
    text = yaml_path.read_text(encoding="utf-8")
    return set(MD_PATH_PATTERN.findall(text))


def main() -> int:
    missing: list[tuple[str, str]] = []
    checked: set[str] = set()

    for yaml_file in collect_yaml_files():
        for rel_path in sorted(extract_md_paths(yaml_file)):
            if rel_path in checked:
                continue
            checked.add(rel_path)
            full = REPO_ROOT / rel_path.replace("/", "\\") if sys.platform == "win32" else REPO_ROOT / rel_path
            # Path handles both separators
            full = REPO_ROOT / Path(rel_path)
            if not full.is_file():
                missing.append((rel_path, yaml_file.relative_to(REPO_ROOT).as_posix()))

    if missing:
        print("Missing markdown paths referenced in Registry:", file=sys.stderr)
        for rel_path, source in missing:
            print(f"  - {rel_path}  (from {source})", file=sys.stderr)
        print(f"\nTotal missing: {len(missing)}", file=sys.stderr)
        return 1

    print(f"All registry markdown paths exist. ({len(checked)} paths checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
