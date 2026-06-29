#!/usr/bin/env python3
"""启动 Release 010 Mock 主窗口 UI。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nfs_scanner_pro.main import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
