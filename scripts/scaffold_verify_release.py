#!/usr/bin/env python3
"""Release 验收脚手架生成器 — Release_033。"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
DOCS_RELEASE = ROOT / "docs/product-spec/release"
PRODUCT_README = ROOT / "docs/product-spec/README.md"
AI_INDEX = ROOT / "spec/AI_INDEX.md"
RELEASE_YAML = ROOT / "spec/Registry/Release.yaml"
VERIFY_ALL = SCRIPTS / "verify_all.py"


class ScaffoldError(Exception):
    pass


@dataclass(frozen=True)
class ReleaseScaffoldConfig:
    release_num: int
    release_id: str
    title: str
    slug: str
    dir_name: str
    verify_script: Path
    docs_dir: Path
    readme_path: Path
    acceptance_path: Path


def normalize_release(release: str) -> int:
    digits = re.sub(r"\D", "", str(release).strip())
    if not digits:
        raise ScaffoldError(f"invalid --release: {release!r}")
    value = int(digits)
    if value < 1 or value > 999:
        raise ScaffoldError(f"--release out of range: {value}")
    return value


def make_slug(name: str) -> str:
    parts = re.split(r"[\s\-/]+", name.strip())
    tokens: list[str] = []
    for part in parts:
        token = re.sub(r"[^A-Za-z0-9]", "", part)
        if not token:
            continue
        if token.isupper() and len(token) <= 4:
            tokens.append(token)
        elif len(token) == 1:
            tokens.append(token.upper())
        else:
            tokens.append(token[0].upper() + token[1:])
    if not tokens:
        raise ScaffoldError(f"cannot derive slug from name: {name!r}")
    return "_".join(tokens)


def build_config(
    release_num: int,
    *,
    title: str,
    slug: str | None = None,
) -> ReleaseScaffoldConfig:
    release_id = f"{release_num:03d}"
    resolved_slug = slug or make_slug(title)
    dir_name = f"Release_{release_id}_{resolved_slug}"
    docs_dir = DOCS_RELEASE / dir_name
    return ReleaseScaffoldConfig(
        release_num=release_num,
        release_id=release_id,
        title=title,
        slug=resolved_slug,
        dir_name=dir_name,
        verify_script=SCRIPTS / f"verify_release_{release_id}.py",
        docs_dir=docs_dir,
        readme_path=docs_dir / "README.md",
        acceptance_path=docs_dir / "ACCEPTANCE_REPORT.md",
    )


def existing_artifacts(config: ReleaseScaffoldConfig) -> list[Path]:
    hits: list[Path] = []
    if config.verify_script.is_file():
        hits.append(config.verify_script)
    if config.docs_dir.is_dir():
        hits.append(config.docs_dir)
    elif config.readme_path.is_file():
        hits.append(config.readme_path)
    elif config.acceptance_path.is_file():
        hits.append(config.acceptance_path)
    return hits


def render_verify_script(config: ReleaseScaffoldConfig) -> str:
    return f'''#!/usr/bin/env python3
"""Release_{config.release_id} 自动验收 — {config.title}。"""

from __future__ import annotations

import compileall
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import verification_report  # noqa: E402
import verification_runtime  # noqa: E402
from verification_utils import (  # noqa: E402
    FORBIDDEN_PATTERNS,
    MOCK_DEVICE_DIRS,
    ROOT as UTILS_ROOT,
    setup_path,
)


def check_compileall(report: verification_report.VerificationReport) -> None:
    report.start_check("compileall")
    ok = bool(compileall.compile_dir(str(ROOT / "src" / "nfs_scanner_pro"), quiet=1))
    if ok:
        report.pass_check("compileall")
    else:
        report.fail_check("compileall")


def check_runtime_isolation(report: verification_report.VerificationReport) -> None:
    report.start_check("runtime_isolation")
    runtime_dir = verification_runtime.get_current_release_runtime()
    ok = runtime_dir is not None and runtime_dir.is_dir()
    if ok:
        rel = runtime_dir.relative_to(ROOT).as_posix()
        report.pass_check("runtime_isolation", rel)
    else:
        report.fail_check("runtime_isolation", "NFS_SCANNER_RUNTIME_DIR not active")


def check_gitignore_runtime(report: verification_report.VerificationReport) -> None:
    report.start_check("gitignore_runtime")
    ok, detail = verification_runtime.assert_runtime_ignored_by_git()
    if ok:
        report.pass_check("gitignore_runtime", detail)
    else:
        report.fail_check("gitignore_runtime", detail)


def check_no_real_device_access(report: verification_report.VerificationReport) -> None:
    report.start_check("no_real_device_access")
    hits: list[str] = []
    for base in MOCK_DEVICE_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in text:
                    hits.append(f"{{path.relative_to(UTILS_ROOT)}}: {{pattern}}")
    if hits:
        report.fail_check("no_real_device_access", "; ".join(hits))
    else:
        report.pass_check("no_real_device_access")


def check_no_high_fidelity_changes(report: verification_report.VerificationReport) -> None:
    report.start_check("no_high_fidelity_changes")
    proc = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    bad = [
        line.strip()
        for line in proc.stdout.splitlines()
        if line.strip().startswith("prototypes/high_fidelity/")
    ]
    if bad:
        report.fail_check("no_high_fidelity_changes", ", ".join(bad))
    else:
        report.pass_check("no_high_fidelity_changes")


def write_acceptance_report(report: verification_report.VerificationReport) -> Path:
    out = (
        ROOT
        / "docs/product-spec/release/{config.dir_name}/ACCEPTANCE_REPORT.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_{config.release_id} 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_{config.release_id}.py",
        "python scripts/verify_all.py --only {config.release_id}",
        "```",
        "",
        "## 检查项",
        "",
    ]
    for name, ok, detail, elapsed, skipped in report.entries:
        status = "SKIP" if skipped else ("PASS" if ok else "FAIL")
        suffix = f" — {{detail}}" if detail else ""
        timing = f" ({{elapsed:.2f}}s)" if elapsed is not None else ""
        lines.append(f"- [{{status}}] `{{name}}`{{timing}}{{suffix}}")
    lines.extend(
        [
            "",
            "## 结果",
            "",
            "PASS" if report.is_pass() else "FAIL",
            "",
            "## runtime 隔离路径",
            "",
            f"- `runtime/verification/R{config.release_id}/`",
            "",
            "## 是否接真实设备",
            "",
            "否",
            "",
            "## 是否生成真实 PDF / Word / Excel",
            "",
            "否",
            "",
            "## 是否修改 high_fidelity HTML",
            "",
            "否",
            "",
            "## 是否可以提交",
            "",
            "是" if report.is_pass() else "否",
            "",
        ]
    )
    out.write_text("\\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    setup_path()
    verification_runtime.enter_release_runtime("R{config.release_id}")
    report = verification_report.VerificationReport("{config.release_id}")

    check_compileall(report)
    check_runtime_isolation(report)
    check_gitignore_runtime(report)
    check_no_real_device_access(report)
    check_no_high_fidelity_changes(report)

    report_path = write_acceptance_report(report)
    report.print_report()  # RESULT: PASS | RESULT: FAIL
    print(f"\\nAcceptance report: {{report_path.relative_to(ROOT)}}")
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
'''


def render_readme(config: ReleaseScaffoldConfig) -> str:
    return f"""# Release {config.release_id} — {config.title}

## 1. Release 目标

{config.title} 的基础 Mock 验收脚本与文档骨架（由 `scaffold_verify_release.py` 生成）。

## 2. 为什么需要本 Release

（在此填写业务或工程动机。）

## 3. 本次实现范围

- `scripts/verify_release_{config.release_id}.py` — 基础验收模板
- `runtime/verification/R{config.release_id}/` — 隔离 runtime
- 标准检查：compileall、runtime 隔离、gitignore、无真实设备访问、无 high_fidelity 改动

## 4. 本次不做什么

- ❌ 不接真实设备 / 不打开串口 / 不发送 SCPI
- ❌ 不实现真实扫描算法
- ❌ 不生成真实 PDF / Word / Excel
- ❌ 不改 high_fidelity HTML / 主窗口布局

## 5. 验收脚本

`scripts/verify_release_{config.release_id}.py`

## 6. 本地运行方式

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_{config.release_id}.py
python scripts/verify_all.py --only {config.release_id}
```

## 7. CI 运行方式

GitHub Actions 执行全量 `python scripts/verify_all.py`，本 Release 已注册。

## 8. 验收标准

- `RESULT: PASS`
- 所有 `[PASS]` 检查项通过
- runtime 数据仅写入 `runtime/verification/R{config.release_id}/`

## 9. 后续 Release 约束

1. 在本模板基础上追加 Release 特定检查，勿硬编码 `runtime/mock_projects`。
2. 使用 `verification_runtime.enter_release_runtime("R{config.release_id}")` 或 `NFS_SCANNER_RUNTIME_DIR`。
3. 新 Release 优先通过 `python scripts/scaffold_verify_release.py` 生成骨架。
"""


def render_acceptance_template(config: ReleaseScaffoldConfig) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""# Release_{config.release_id} 验收报告

## 执行时间

{now}

## 执行命令

```bash
python scripts/verify_release_{config.release_id}.py
python scripts/verify_all.py --only {config.release_id}
```

## 检查项

- （运行验收脚本后自动更新）

## 结果

（待验收）

## runtime 隔离路径

- `runtime/verification/R{config.release_id}/`

## 是否接真实设备

否

## 是否生成真实 PDF / Word / Excel

否

## 是否修改 high_fidelity HTML

否

## 是否可以提交

否（待首次验收 PASS）
"""


def insert_verify_all_entry(text: str, config: ReleaseScaffoldConfig) -> tuple[str, bool]:
    marker = f'verify_release_{config.release_id}.py'
    if marker in text:
        return text, False

    new_line = (
        f'    ({config.release_num}, "Release {config.release_id}", '
        f'SCRIPTS / "verify_release_{config.release_id}.py"),'
    )
    lines = text.splitlines(keepends=True)
    in_tuple = False
    insert_at: int | None = None
    for index, line in enumerate(lines):
        if "VERIFY_SCRIPTS:" in line and "= (" in line:
            in_tuple = True
            continue
        if not in_tuple:
            continue
        match = re.match(r"\s+\((\d+),", line)
        if match:
            if int(match.group(1)) < config.release_num:
                insert_at = index + 1
        elif line.strip() == ")":
            if insert_at is None:
                insert_at = index
            break
    if insert_at is None:
        raise ScaffoldError("无法安全更新 verify_all.py：找不到 VERIFY_SCRIPTS 插入点")
    lines.insert(insert_at, new_line + "\n")
    return "".join(lines), True


def remove_verify_all_entry(text: str, config: ReleaseScaffoldConfig) -> tuple[str, bool]:
    marker = f'verify_release_{config.release_id}.py'
    if marker not in text:
        return text, False
    pattern = (
        rf'^\s+\({config.release_num}, "Release {config.release_id}", '
        rf'SCRIPTS / "verify_release_{config.release_id}\.py"\),\n'
    )
    new_text, count = re.subn(pattern, "", text, count=1, flags=re.MULTILINE)
    if count == 0:
        raise ScaffoldError(f"无法从 verify_all.py 移除 Release {config.release_id}")
    return new_text, True


def insert_product_readme_row(text: str, config: ReleaseScaffoldConfig) -> tuple[str, bool]:
    link = f"release/{config.dir_name}/README.md"
    row = (
        f"| Release {config.release_id} | {config.title} | "
        f"[release/{config.dir_name}/README.md]({link}) |"
    )
    if config.dir_name in text:
        return text, False
    anchor = "| Release 032 |"
    pos = text.find(anchor)
    if pos == -1:
        return text.rstrip() + "\n" + row + "\n", True
    line_end = text.find("\n", pos)
    if line_end == -1:
        return text + "\n" + row + "\n", True
    return text[: line_end + 1] + row + "\n" + text[line_end + 1 :], True


def remove_product_readme_row(text: str, config: ReleaseScaffoldConfig) -> tuple[str, bool]:
    if config.dir_name not in text:
        return text, False
    pattern = rf"^\| Release {config.release_id} \|.*{re.escape(config.dir_name)}.*\|\n"
    new_text, count = re.subn(pattern, "", text, count=1, flags=re.MULTILINE)
    return new_text, count > 0


def insert_ai_index_section(text: str, config: ReleaseScaffoldConfig) -> tuple[str, bool]:
    if config.dir_name in text:
        return text, False
    section = f"""
### 5.1 做 {config.title}（Release {config.release_id}）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/{config.dir_name}/README.md
→ scripts/verify_release_{config.release_id}.py
→ scripts/scaffold_verify_release.py
```
"""
    anchor = "### 5.2 做领域模型"
    pos = text.find(anchor)
    if pos == -1:
        return text.rstrip() + section + "\n", True
    return text[:pos] + section + "\n" + text[pos:], True


def remove_ai_index_section(text: str, config: ReleaseScaffoldConfig) -> tuple[str, bool]:
    if config.dir_name not in text:
        return text, False
    pattern = (
        rf"\n### 5\.1[^\n]*Release {config.release_id}[^\n]*\n\n```text\n"
        rf"[\s\S]*?```\n"
    )
    new_text, count = re.subn(pattern, "\n", text, count=1)
    return new_text, count > 0


def insert_release_yaml_entry(text: str, config: ReleaseScaffoldConfig) -> tuple[str, bool]:
    entry = f"    - docs/product-spec/release/{config.dir_name}/README.md"
    if config.dir_name in text:
        return text, False
    anchor = "Release_032_Migrate_Legacy_Verify_Scripts_To_Isolated_Runtime/README.md"
    pos = text.find(anchor)
    if pos == -1:
        return text.rstrip() + "\n" + entry + "\n", True
    line_end = text.find("\n", pos)
    return text[: line_end + 1] + entry + "\n" + text[line_end + 1 :], True


def remove_release_yaml_entry(text: str, config: ReleaseScaffoldConfig) -> tuple[str, bool]:
    if config.dir_name not in text:
        return text, False
    pattern = rf"^\s+- docs/product-spec/release/{re.escape(config.dir_name)}/README\.md\n"
    new_text, count = re.subn(pattern, "", text, count=1, flags=re.MULTILINE)
    return new_text, count > 0


@dataclass
class PlannedChanges:
    create: list[Path]
    update: list[Path]
    config: ReleaseScaffoldConfig


def plan_changes(config: ReleaseScaffoldConfig) -> PlannedChanges:
    create = [config.verify_script, config.readme_path, config.acceptance_path]
    update = [VERIFY_ALL, PRODUCT_README, AI_INDEX, RELEASE_YAML]
    return PlannedChanges(create=create, update=update, config=config)


def apply_scaffold(config: ReleaseScaffoldConfig, *, dry_run: bool = False) -> list[str]:
    actions: list[str] = []
    verify_text = render_verify_script(config)
    readme_text = render_readme(config)
    acceptance_text = render_acceptance_template(config)

    actions.append(f"CREATE {config.verify_script.relative_to(ROOT)}")
    actions.append(f"CREATE {config.readme_path.relative_to(ROOT)}")
    actions.append(f"CREATE {config.acceptance_path.relative_to(ROOT)}")

    if dry_run:
        actions.append(f"UPDATE {VERIFY_ALL.relative_to(ROOT)}")
        actions.append(f"UPDATE {PRODUCT_README.relative_to(ROOT)}")
        actions.append(f"UPDATE {AI_INDEX.relative_to(ROOT)}")
        actions.append(f"UPDATE {RELEASE_YAML.relative_to(ROOT)}")
        return actions

    config.docs_dir.mkdir(parents=True, exist_ok=True)
    config.verify_script.write_text(verify_text, encoding="utf-8")
    config.readme_path.write_text(readme_text, encoding="utf-8")
    config.acceptance_path.write_text(acceptance_text, encoding="utf-8")

    verify_all_text = VERIFY_ALL.read_text(encoding="utf-8")
    verify_all_text, _ = insert_verify_all_entry(verify_all_text, config)
    VERIFY_ALL.write_text(verify_all_text, encoding="utf-8")
    actions.append(f"UPDATE {VERIFY_ALL.relative_to(ROOT)}")

    product_text = PRODUCT_README.read_text(encoding="utf-8")
    product_text, _ = insert_product_readme_row(product_text, config)
    PRODUCT_README.write_text(product_text, encoding="utf-8")
    actions.append(f"UPDATE {PRODUCT_README.relative_to(ROOT)}")

    ai_text = AI_INDEX.read_text(encoding="utf-8")
    ai_text, _ = insert_ai_index_section(ai_text, config)
    AI_INDEX.write_text(ai_text, encoding="utf-8")
    actions.append(f"UPDATE {AI_INDEX.relative_to(ROOT)}")

    yaml_text = RELEASE_YAML.read_text(encoding="utf-8")
    yaml_text, _ = insert_release_yaml_entry(yaml_text, config)
    RELEASE_YAML.write_text(yaml_text, encoding="utf-8")
    actions.append(f"UPDATE {RELEASE_YAML.relative_to(ROOT)}")

    return actions


def remove_scaffold(config: ReleaseScaffoldConfig, *, dry_run: bool = False) -> list[str]:
    actions: list[str] = []
    if config.verify_script.is_file():
        actions.append(f"DELETE {config.verify_script.relative_to(ROOT)}")
        if not dry_run:
            config.verify_script.unlink()
    if config.docs_dir.is_dir():
        actions.append(f"DELETE {config.docs_dir.relative_to(ROOT)}/")
        if not dry_run:
            import shutil

            shutil.rmtree(config.docs_dir)

    if dry_run:
        actions.extend(
            [
                f"UPDATE {VERIFY_ALL.relative_to(ROOT)}",
                f"UPDATE {PRODUCT_README.relative_to(ROOT)}",
                f"UPDATE {AI_INDEX.relative_to(ROOT)}",
                f"UPDATE {RELEASE_YAML.relative_to(ROOT)}",
            ]
        )
        return actions

    verify_all_text = VERIFY_ALL.read_text(encoding="utf-8")
    verify_all_text, _ = remove_verify_all_entry(verify_all_text, config)
    VERIFY_ALL.write_text(verify_all_text, encoding="utf-8")
    actions.append(f"UPDATE {VERIFY_ALL.relative_to(ROOT)}")

    product_text = PRODUCT_README.read_text(encoding="utf-8")
    product_text, _ = remove_product_readme_row(product_text, config)
    PRODUCT_README.write_text(product_text, encoding="utf-8")
    actions.append(f"UPDATE {PRODUCT_README.relative_to(ROOT)}")

    ai_text = AI_INDEX.read_text(encoding="utf-8")
    ai_text, _ = remove_ai_index_section(ai_text, config)
    AI_INDEX.write_text(ai_text, encoding="utf-8")
    actions.append(f"UPDATE {AI_INDEX.relative_to(ROOT)}")

    yaml_text = RELEASE_YAML.read_text(encoding="utf-8")
    yaml_text, _ = remove_release_yaml_entry(yaml_text, config)
    RELEASE_YAML.write_text(yaml_text, encoding="utf-8")
    actions.append(f"UPDATE {RELEASE_YAML.relative_to(ROOT)}")

    return actions


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate verify_release_NNN.py and Release documentation skeleton.",
    )
    parser.add_argument(
        "--release",
        required=True,
        help="Release number (e.g. 034 or 34)",
    )
    parser.add_argument(
        "--name",
        default="",
        help='Human-readable name, e.g. "Project Workspace UI Verification"',
    )
    parser.add_argument(
        "--title",
        default="",
        help="Optional title (defaults to --name)",
    )
    parser.add_argument(
        "--slug",
        default="",
        help="Optional directory slug (defaults to derived from name)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned files without writing",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove scaffold artifacts for the given release (internal cleanup)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    release_num = normalize_release(args.release)
    title = (args.title or args.name).strip()
    if not title:
        print("error: --name or --title is required", file=sys.stderr)
        return 2

    slug = args.slug.strip() or None
    config = build_config(release_num, title=title, slug=slug)

    if args.remove:
        actions = remove_scaffold(config, dry_run=args.dry_run)
        for action in actions:
            print(action)
        print(f"\nRemoved Release {config.release_id} scaffold artifacts.")
        return 0

    existing = existing_artifacts(config)
    if existing and not args.force:
        paths = ", ".join(str(p.relative_to(ROOT)) for p in existing)
        print(f"error: target already exists ({paths}); use --force to overwrite", file=sys.stderr)
        return 1

    if args.dry_run:
        actions = apply_scaffold(config, dry_run=True)
        for action in actions:
            print(action)
        print(f"\nDry run OK — Release {config.release_id} ({config.dir_name})")
        return 0

    if existing and args.force:
        remove_scaffold(config)

    actions = apply_scaffold(config)
    for action in actions:
        print(action)
    print(f"\nScaffold created for Release {config.release_id}: {config.title}")
    print(f"  verify: scripts/verify_release_{config.release_id}.py")
    print(f"  docs:   docs/product-spec/release/{config.dir_name}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
