# ServoSystem — 探头舵机

## 1. 对象定义
可选 Hx/Hy 探头切换舵机。

## 2. 为什么需要
ADR-0004 整区切换通道时的物理姿态。

## 3. 关键字段
connectionState, hxPosition, hyPosition, currentChannel。

## 4–5. 关系
Probe 切换；HxHyCalibration。

## 6–7. 状态
[Servo_State_Machine.md](../04_State_Machines/Servo_State_Machine.md)

## 8–9. 映射/UI
Snapshot；deviceStatusServoIndicator。

## 10. Qt
切换命令队列；与 ScanTask 状态互锁。

## 11. 禁止
禁止切换中启动 ScanTask。

## 相关
[Servo_Error_Recovery.md](../06_Error_Recovery/Servo_Error_Recovery.md)
