# ScanTask — 扫描任务

## 1. 对象定义

ScanTask 表示 Region 下 **一次完整采集执行**（历史 `Scan`），含路径、逐点数据、设备快照与状态机。

## 2. 为什么需要这个对象

- 可追溯每次扫描参数与设备态（ADR-0007）
- Hx / Hy 分任务存储
- 重扫不覆盖 raw data

## 3. 关键字段

| 字段 | 说明 |
|---|---|
| scanTaskId | UUID |
| projectId, regionId, pcbId | 三元上下文 |
| probe | Probe（Hx/Hy） |
| deviceSnapshotId | 开始时冻结 |
| status | 状态机当前态 |
| stepX, stepY, z, dwell, frequency… | 参数副本 |
| pointCount, startedAt, finishedAt | |
| errorCode, errorMessage | 失败时 |

## 4. 所属关系

- 属于 Region → Project

## 5. 与其它对象关系

- 1:1 Probe（通道）
- 1:1 DeviceSnapshot（任务级）
- 1:N ScanPoint
- 0:N FrequencyData（按点或迹线）
- 0:N Heatmap（处理后）
- 0:N Analysis

**必须绑定**：Project + PCB + Region + Probe + DeviceSnapshot。

## 6. 生命周期

见 [ScanTask_Lifecycle.md](../05_Lifecycle/ScanTask_Lifecycle.md)。

## 7. 状态

见 [Scan_State_Machine.md](../04_State_Machines/Scan_State_Machine.md)：Pending → Running ⇄ Paused → Completed | Failed | Cancelled。

## 8. 文件系统映射

```text
{region}/scans/{scanTaskId}/
  scan.json
  raw/
  processed/
```

## 9. UI 映射

- 工具栏开始/停止
- statusBar 进度、Breadcrumb 点数
- 扫描中锁定 regionSettings 部分字段

## 10. Qt/PySide6 实现建议

- `ScanTaskController` 状态机
- 信号：progressUpdated, stateChanged, completed

## 11. 禁止事项

- 禁止覆盖 raw 目录
- 禁止 Camera 离线阻止创建/运行
- 禁止 V1 每点切换 Hx/Hy（ADR-0004）

## 相关

- 历史：[../../data/Scan.md](../../data/Scan.md)
