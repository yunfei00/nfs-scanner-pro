# ScanTask Lifecycle — 扫描任务生命周期

> 从业务视角描述 ScanTask **端到端**阶段（非仅状态机）。与 [Scan_State_Machine.md](../04_State_Machines/Scan_State_Machine.md) 配合使用。

## 生命周期流程

```text
创建任务
  ↓
冻结设备快照（DeviceSnapshot）
  ↓
生成扫描路径（ScanPoint 序列）
  ↓
执行扫描（状态机：准备就绪 → 扫描中 → …）
  ↓
保存采样点（raw/points.csv 等）
  ↓
生成热力图（Heatmap，可异步）
  ↓
进入分析（Analysis）
  ↓
生成报告（Report，可选）
  ↓
归档（Archived，随 Project）
```

## 各阶段说明

| 阶段 | 持久化 | 失败处理 |
|---|---|---|
| 创建任务 | `scans/{id}/scan.json` status=Created | — |
| 冻结快照 | `devices/snapshots/{id}.json` locked | 未冻结禁止 Scanning |
| 生成路径 | scan.json pointCount, path preview | 参数非法→未就绪 |
| 执行扫描 | raw/ 增量写入 | 见 Scan_Error_Recovery |
| 保存采样点 | raw 完整 | 磁盘满→Error |
| 生成热力图 | processed/heatmap_* | 失败可重试，不删 raw |
| 进入分析 | analysis/*.json | 可 regenerate |
| 生成报告 | reports/* | 只读引用 |
| 归档 | project lifecycle Archived | 只读 |

## Region 生命周期交叉

Region 在首次 ScanTask Completed 后进入「已扫描」阶段（见 [Region_Lifecycle.md](Region_Lifecycle.md)）。

## 相关

- [ScanTask.md](../02_Core_Objects/ScanTask.md)
- [Heatmap_Lifecycle.md](Heatmap_Lifecycle.md)
