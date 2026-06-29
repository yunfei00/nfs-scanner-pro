# Servo State Machine — 舵机子系统状态机

## 1. 状态列表
Disabled | Disconnected | Ready | Switching | Error

## 2–3. Switching(Hx|Hy) 期间禁止 ScanTask start。

## 4–8. UI/日志/恢复
[Servo_Error_Recovery.md](../06_Error_Recovery/Servo_Error_Recovery.md)；切换失败 → Alignment 可能需重新确认。
