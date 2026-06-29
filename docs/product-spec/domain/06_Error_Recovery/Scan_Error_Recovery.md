# Scan Error Recovery — 扫描任务异常恢复

## 异常场景与处理

| 场景 | 处理 | UI |
|---|---|---|
| **扫描中途停止** | → Stopping → Completed(partial) 或 Cancelled；**保留 raw** | 停止钮；确认 Dialog |
| **扫描中设备断开** | → Paused；[Device_Error_Recovery](Device_Error_Recovery.md) | 红 statusBar |
| **数据点缺失** | 标记 ScanPoint Skipped；可继续或暂停 | 表格+日志 |
| **文件保存失败** | → Error；已写部分保留 | 磁盘满提示 |
| **断点续扫** | 读 resumeIndex；路径跳过已采点 | Dialog「从第 N 点继续」 |
| **扫描完成但热力图失败** | ScanTask=Completed；Heatmap=Stale | statusBar「热力图生成失败，可重试」 |

## 断点续扫字段（scan.json）

```text
resumeIndex: number
partial: boolean
lastSavedPointAt: datetime
```

## 崩溃恢复

启动 Project 时扫描 `scans/*/scan.json`：

- status=Scanning → 提示恢复/标记 Error
- 写 `logs/recovery.log`

## 禁止

- 中途停止删 raw
- 热力图失败回滚 Completed

## 相关

[Scan_State_Machine.md](../04_State_Machines/Scan_State_Machine.md)
