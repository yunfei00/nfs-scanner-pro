#!/usr/bin/env python3
"""生成首次联调模板 — Release 048（不连接设备）。"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.app_paths import get_runtime_dir

CHECKLIST = """# 首次联调 Checklist

## 准备（用户填写）

- [ ] 操作员：________________
- [ ] 日期：________________
- [ ] 运动平台端口：________________
- [ ] 频谱仪 IP：________________
- [ ] 相机索引：________________
- [ ] 舵机端口：________________

## 执行顺序

1. [ ] `python scripts/validate_commissioning_readiness.py`
2. [ ] `python scripts/start_hardware_commissioning.py --mode offline`
3. [ ] `python scripts/start_hardware_commissioning.py --mode fake`
4. [ ] 设置 NFS_ENABLE_REAL_HARDWARE=1 后 `--mode real-safe`（仅安全探测）

## 禁止项

- 不跳过 manual confirm 步骤
- 不默认 real-run
"""

RECORD = """# 首次联调结果记录

| 步骤 | PASS/FAIL | 备注 |
|------|-----------|------|
| 环境检查 | | |
| 配置检查 | | |
| 运动 status | | |
| 频谱 IDN | | |
| fake-run | | |
| real-run gate | | |

## 故障记录

（在此填写 failure_records 摘要）

## 签字

- 操作员：________________
- 复核：________________
"""


def _output_dir() -> Path:
    runtime = get_runtime_dir()
    if "verification" in runtime.parts:
        directory = runtime / "commissioning_template"
    else:
        directory = runtime / "commissioning_templates"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def main() -> int:
    out = _output_dir()
    hw_src = ROOT / "config" / "hardware.local.example.yaml"
    cm_src = ROOT / "config" / "commissioning.local.example.yaml"
    shutil.copy2(hw_src, out / "hardware.local.yaml.template")
    shutil.copy2(cm_src, out / "commissioning.local.yaml.template")
    (out / "first-bringup-checklist.md").write_text(CHECKLIST, encoding="utf-8")
    (out / "first-bringup-result-record.md").write_text(RECORD, encoding="utf-8")
    print(f"Templates written to: {out}")
    for name in (
        "hardware.local.yaml.template",
        "commissioning.local.yaml.template",
        "first-bringup-checklist.md",
        "first-bringup-result-record.md",
    ):
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
