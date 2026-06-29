# Motion State Machine — 运动子系统状态机

## 1. 状态列表
Disconnected | Connecting | Ready | Moving | Error | Homing

## 2–3. 说明与转换
| 从 | 事件 | 到 |
|---|---|---|
| Disconnected | connect | Connecting |
| Connecting | ok | Ready |
| Ready | move | Moving |
| Moving | done | Ready |
| * | fault | Error |
| Ready | home | Homing → Ready |

ScanTask Scanning 时 Motion=Moving/Busy。

## 4–5. 允许/禁止
允许：Ready 时记录起终点。禁止：Moving 时 disconnect。

## 6. UI
deviceStatusMotionIndicator；设备页坐标。

## 7. 日志
device.log ERROR on fault

## 8. 错误恢复
[Motion_Error_Recovery.md](../06_Error_Recovery/Motion_Error_Recovery.md)
