# Domain Event Model — 领域事件

> 解耦 Domain / UI / 日志。Release 010 可用 Qt 信号或 EventBus 实现。

## 事件总表

| 事件名 | 触发时机 | 主要载荷 | UI 响应 | 写日志 |
|---|---|---|---|---|
| **ProjectOpened** | 文件→打开成功 | projectId, path | 加载画布/Region | INFO domain.log |
| **ProjectClosed** | 文件→关闭 | projectId | 清空 UI | INFO |
| **ProjectSaved** | Ctrl+S | projectId, path | statusBar「已保存」 | INFO |
| **RegionCreated** | 新建 Region | regionId, name | 画布新矩形 | INFO |
| **RegionUpdated** | 改范围/名 | regionId, fields | 刷新层/Breadcrumb | INFO |
| **RegionSelected** | 用户选中 | regionId | Breadcrumb/Dock | DEBUG |
| **AlignmentUpdated** | 确认/修改对齐 | regionId, status | 矩形样式 | INFO alignment log |
| **DeviceConnected** | connect OK | deviceType | 绿点 | INFO device.log |
| **DeviceDisconnected** | 断开 | deviceType, reason | 灰/红点 | WARN |
| **DeviceError** | 命令失败 | deviceType, code | statusBar+logDock | ERROR |
| **ScanStarted** | Ready→Scanning | scanTaskId, snapshotId | 锁参/进度 | INFO scan log |
| **ScanPointMeasured** | 单点完成 | scanTaskId, index, value | 进度/表格节流 | DEBUG |
| **ScanPaused** | 暂停 | scanTaskId, reason | 黄 statusBar | WARN |
| **ScanStopped** | 停止中 | scanTaskId | 灰「停止中」 | INFO |
| **ScanCompleted** | 已完成 | scanTaskId, pointCount | 绿 statusBar | INFO |
| **ScanFailed** | 错误 | scanTaskId, code | 红 statusBar | ERROR |
| **HeatmapGenerated** | PNG 就绪 | scanTaskId, heatmapId, path | 刷新 heatmapLayer | INFO |
| **AnalysisGenerated** | 分析完成 | analysisId | 分析页 | INFO |
| **ReportGenerated** | 报告就绪 | reportId, format | 报告页 | INFO |

## 载荷字段规范（示例）

```text
ScanStarted {
  scanTaskId: string
  regionId: string
  probeChannel: "Hx" | "Hy"
  deviceSnapshotId: string
  pointCount: number
  timestamp: ISO8601
}
```

## 订阅建议

| 订阅者 | 事件 |
|---|---|
| MainWindow / statusBar | Scan* , Device* |
| scanCanvasView | Region*, Alignment*, HeatmapGenerated |
| logDock | DeviceError, ScanFailed, *Recovery |
| scanParamDock | RegionSelected, ScanStarted/Completed |

## 日志

- 全局：`logs/domain.log`
- 扫描：`logs/scan_{scanTaskId}.log`
- 凡表中「写日志=INFO 及以上」者必须落盘

## 禁止

- UI 直接写盘不经过 Domain Service
- 无载荷的 ScanCompleted

## 相关

[Domain_To_Qt_Model_Mapping.md](Domain_To_Qt_Model_Mapping.md)
