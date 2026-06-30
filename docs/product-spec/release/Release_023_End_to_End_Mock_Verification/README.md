# Release 023 — End-to-End Mock Verification Suite

## 1. Release 目标

建立 **全项目自动验收基座**，使每个 Release 可通过 `verify_release_xxx.py` 独立验收，并通过 `verify_all.py` 统一运行。

## 2. 为什么需要全流程自动验收

- Release 011~022 已形成 Mock 扫描 → 持久化 → 分析 → 报告链路。
- 人工点击 UI 验收不可持续；后续 Release 必须由脚本自动验证。
- 统一入口可在 CI / 本地一键确认主线能力未回归。

## 3. 本次实现范围

- `scripts/verification_utils.py` — 共享验收工具
- `scripts/verify_release_023.py` — 端到端 Mock 验收
- `scripts/verify_all.py` — 运行 022 + 023 验收脚本
- Release 文档与 ACCEPTANCE_REPORT

## 4. 本次不做什么

- ❌ 不接真实设备 / 串口 / SCPI / 相机
- ❌ 不生成真实 PDF / Word / Excel
- ❌ 不修改 high_fidelity HTML
- ❌ 不改主窗口布局 / 导航结构
- ❌ 不增加新业务功能

## 5. 验收脚本说明

| 脚本 | 用途 |
|---|---|
| `verify_release_022.py` | 报告数据源 Mock 专项验收 |
| `verify_release_023.py` | 全链路端到端 Mock 验收 |
| `verify_all.py` | 统一运行上述脚本 |

## 6. verify_release_023.py 检查项

- compileall + 核心模块 import
- .gitignore（runtime / pycache）
- MainWindow offscreen（单 Dock、页面 Dock 映射、工具栏）
- Project Mock / Workspace Persistence
- DeviceManagerMock / ScanEngineMock
- Scan Result Persistence / Analysis / Report 数据源
- 禁止真实外设访问字符串

## 7. verify_all.py 用法

```bash
python scripts/verify_all.py
```

输出示例：

```text
Verification Suite

Release 022: PASS
Release 023: PASS

RESULT: PASS
```

## 8. 后续 Release 约束

1. 每个新 Release **必须** 提供 `scripts/verify_release_XXX.py`。
2. 新脚本 **必须** 加入 `verify_all.py` 的 `VERIFY_SCRIPTS` 列表。
3. 验收使用 `QT_QPA_PLATFORM=offscreen`，禁止真实外设。
4. 验收通过后方可 commit / push（用户授权自动化流程）。

## 9. 验收标准

- [ ] `python scripts/verify_release_023.py` → RESULT: PASS
- [ ] `python scripts/verify_all.py` → RESULT: PASS
- [ ] `compileall` 通过
- [ ] runtime 数据不进 Git
- [ ] 无真实 PDF / Word / Excel 输出

## 10. 后续 Release_024 建议

- CI 集成 `verify_all.py`（GitHub Actions）
- 扫描页 offscreen 交互验收（开始/停止 Mock 扫描）
- 报告页 offscreen 新建草稿验收
