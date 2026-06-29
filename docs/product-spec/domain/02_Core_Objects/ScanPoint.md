# ScanPoint — 扫描点

## 1. 对象定义
ScanTask 路径上的 **单个采集点**（坐标 + 测量值索引）。

## 2. 为什么需要
路径预览、进度、raw 数据行、表格 Dock。

## 3. 关键字段
index, x, y, z, status, measuredAt, frequencyDataRef, valueDbuVpm。

## 4. 所属关系
属于 ScanTask。

## 5. 与其它对象关系
1:1 或 1:N FrequencyData；聚合为 Heatmap。

## 6. 生命周期
Pending → Acquired → Skipped | Failed。

## 7. 状态
随 ScanTask 状态机批量推进。

## 8. 文件系统映射
`raw/points.csv` 或 `raw/points/{index}.json`

## 9. UI 映射
pathLayer 点、markerLayer 当前点、dataTableView。

## 10. Qt/PySide6 实现建议
大批量用流式写盘；UI 节流刷新 ≤5Hz。

## 11. 禁止事项
禁止全表常驻内存无上限。

## 相关
[ScanTask.md](ScanTask.md)
