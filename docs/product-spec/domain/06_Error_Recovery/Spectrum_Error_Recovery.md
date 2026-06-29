# Spectrum Error Recovery — 频谱仪异常恢复

## 异常场景与处理

| 场景 | 检测 | ScanTask 动作 | UI | 日志 |
|---|---|---|---|---|
| **频谱仪未连接** | 未 Connected | 未就绪 | 频谱指示红 | ERROR `SPECTRUM_NOT_CONNECTED` |
| **Sweep 超时** | SCPI 无响应 | 单点 Retry×3 → 暂停 | statusBar 警告 | WARN `SPECTRUM_SWEEP_TIMEOUT` |
| **Trace 不存在** | `TRAC?` 空/错误 | 暂停；提示改迹线 | instrumentSettings 高亮 | ERROR `SPECTRUM_TRACE_MISSING` |
| **数据为空** | 读数全 NaN | 标记 ScanPoint Skip | 表格该行灰 | WARN `SPECTRUM_EMPTY_TRACE` |
| **频率点不匹配** | 设定 vs 读回偏差 | 暂停或 Skip 点 | 显示偏差值 | WARN `SPECTRUM_FREQ_MISMATCH` |
| **SCPI 返回错误** | `+100,...` | 暂停/Error | logDock 全文 | ERROR `SPECTRUM_SCPI_{code}` |

## 恢复流程

```text
SCPI 错误
  → 记录命令与响应
  → 尝试 :SYST:ERR? 清队列
  → 重连 Session
  → 用户「继续扫描」从当前 index
```

## 禁止

- Spectrum 未连接时进入 Scanning
- 静默填零代替空 Trace

## 相关

[Spectrum_State_Machine.md](../04_State_Machines/Spectrum_State_Machine.md)
