# Release 024 — Full Workflow Smoke Test

## 1. Release 目标

建立 **端到端冒烟验收** 脚本 `verify_release_024.py`，在 offscreen 模式下自动串联 Project → Workspace → Device → Scan → Analysis → Report 全链路 Mock 工作流。

## 2. 为什么需要端到端冒烟验收

- Release 022/023 分别验证了报告数据源与模块级 Mock，但未验证 **跨页面串联**。
- 单模块 PASS 不能保证页面切换、Dock 映射、扫描落盘后分析/报告可读。
- 冒烟脚本可在每次 Release 前一键确认主线工作流未回归。

## 3. 覆盖范围

| 步骤 | 内容 |
|---|---|
| A | MainWindow offscreen 启动 |
| B | Project Mock 打开/创建 |
| C | Workspace 状态 load/save |
| D | DeviceManagerMock 连接/快照/jog |
| E | ScanEngineMock prepare→start→tick→completed |
| F | ScanResultPersistence 三文件落盘 |
| G | 分析页 Dock + AnalysisDataSource |
| H | 报告页 Dock + ReportDraft 保存 |
| I | 扫描→设备→分析→报告→扫描 回归 |
| J | 禁止真实外设访问字符串 |

## 4. 不做什么

- ❌ 不接真实设备 / 串口 / SCPI / 相机
- ❌ 不生成真实 PDF / Word / Excel
- ❌ 不修改 high_fidelity HTML / 主窗口布局
- ❌ 不新增业务功能

## 5. verify_release_024.py 说明

```bash
python scripts/verify_release_024.py
```

- 设置 `QT_QPA_PLATFORM=offscreen`
- 输出 10 项 `[PASS]`/`[FAIL]` 检查
- exit 0 = PASS，exit 1 = FAIL
- 自动生成 `ACCEPTANCE_REPORT.md`

## 6. verify_all.py 集成

`verify_all.py` 串行执行 022 / 023 / 024，任一 FAIL 则整体 FAIL。

```bash
python scripts/verify_all.py
```

## 7. 验收标准

- [ ] `verify_release_024.py` → RESULT: PASS
- [ ] `verify_all.py` → RESULT: PASS
- [ ] runtime 数据不进 Git
- [ ] 扫描完成 6461 点 Mock 总点数
- [ ] 分析/报告页可读取刚保存的 ScanTask

## 8. 后续 Release 约束

1. 新 Release 必须更新或扩展冒烟脚本（或新增专项 verify）。
2. 任何影响主链路的改动必须在 `verify_all.py` PASS 后提交。
3. 优先修 verify 暴露的 bug，避免大范围重构。

## 9. 后续 Release_025 建议

- **CI 集成**：GitHub Actions 运行 `verify_all.py`
- **扫描页 offscreen 交互**：工具栏开始/停止 Mock 扫描按钮
