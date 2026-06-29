# ADR-0017 Scan State Machine

## 背景
扫描 UI（工具栏/参数锁/statusBar）须与业务一致。Release 009.8 前仅有简略 Pending/Running。

## 决策
采用七态中文模型：

```text
未就绪 → 准备就绪 → 扫描中 ⇄ 暂停 → 停止中 → 已完成
扫描中 → 错误 →（重置）→ 准备就绪
```

每态定义：开始/停止钮、参数可编辑性、设备断开、保存、statusBar 色、日志级别。

## 后果
- Mock UI 与 ScanTaskController 有明确验收表。
- Stopping 为显式态，避免 stop 与 complete 竞态。

## 替代方案
- 仅三态 Idle/Run/Done：否决，无法表达暂停与停止中。
- 每点一态：否决，状态爆炸。

## 与已有 Release 关系
- 009.5 `Scan_State_Interaction` 须与本 ADR 对齐。
- 010 Prototype 首 PR 须实现至少 Ready/Scanning/Completed 三态 UI。

## 相关
[Scan_State_Machine.md](../domain/04_State_Machines/Scan_State_Machine.md)
