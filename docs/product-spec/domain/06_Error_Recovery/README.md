# Error Recovery — 异常恢复总览

| 文档 | 场景要点 |
|---|---|
| [Device_Error_Recovery.md](Device_Error_Recovery.md) | 聚合断开、ScanTask Pause |
| [Motion_Error_Recovery.md](Motion_Error_Recovery.md) | 串口断、回零失败、超程、超时、位置未知、续扫 |
| [Spectrum_Error_Recovery.md](Spectrum_Error_Recovery.md) | 未连接、Sweep 超时、Trace 空、频点不匹配、SCPI 错 |
| [Camera_Error_Recovery.md](Camera_Error_Recovery.md) | 未连接、占用、拍照失败、分辨率变、**可选继续扫** |
| [Servo_Error_Recovery.md](Servo_Error_Recovery.md) | Hx/Hy 切换失败 |
| [Alignment_Error_Recovery.md](Alignment_Error_Recovery.md) | 保存失败、PCB 变更 |
| [Scan_Error_Recovery.md](Scan_Error_Recovery.md) | 中途停、设备断、缺点、写盘失败、续扫、热力图失败 |
| [Data_Error_Recovery.md](Data_Error_Recovery.md) | json 损坏、raw 缺失、CSV 错、Report 源丢失 |

原则：可诊断、可恢复、**不删 raw**、相机不阻断扫描。

UI：[Error_Recovery_Pattern](../../design-system/03_Patterns/Error_Recovery_Pattern.md)
