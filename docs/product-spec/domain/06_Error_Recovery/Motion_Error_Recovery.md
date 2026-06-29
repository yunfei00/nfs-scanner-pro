# Motion Error Recovery — 运动平台异常恢复

## 异常场景与处理

| 场景 | 检测 | ScanTask 动作 | UI | 日志 |
|---|---|---|---|---|
| **串口断开** | read/write 失败 | → 暂停 | 运动指示红；statusBar「串口断开」 | ERROR `MOTION_SERIAL_LOST` |
| **回零失败** | home 超时/报警 | 保持未就绪/暂停 | Dialog 重试回零 | ERROR `MOTION_HOME_FAILED` |
| **超出行程** | 目标超 soft limit | → 错误 | 红框+禁止继续 | ERROR `MOTION_OUT_OF_RANGE` |
| **运动超时** | move 未到位 | 单点 Retry×3 → 暂停 | 黄条「运动超时」 | WARN→ERROR |
| **当前位置未知** | 失步/未 homed | 禁止 Scanning；须回零 | 「请先回零」 | WARN `MOTION_POS_UNKNOWN` |
| **扫描中断恢复** | 启动时 scan.json=Paused | 提示续扫或标记失败 | Dialog 三选一 | INFO `MOTION_RESUME_OFFER` |

## 恢复流程（扫描中断）

```text
检测到 Paused/Scanning 异常退出
  → 读 raw 已有点数
  → 用户选择：从下一点继续 / 放弃并 Completed(partial) / 标记 Error
  → 回零可选（推荐）
  → 写 scan.json resumeIndex
```

## 禁止

- 位置未知时自动继续 Scanning
- 静默丢弃已采 raw

## 相关

[Scan_Error_Recovery.md](Scan_Error_Recovery.md)、[Device_Error_Recovery.md](Device_Error_Recovery.md)
