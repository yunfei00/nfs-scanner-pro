# Camera State Machine — 相机子系统状态机

## 1. 状态列表
Disabled | Disconnected | Connecting | Ready | Capturing | Degraded

## 2–3. 说明
Degraded=拍照失败但可选继续。**不**触发 ScanTask Error。

## 4–5. 允许/禁止
允许 Offline 扫描。禁止 Camera Error 阻断 Scanning。

## 6. UI
指示**灰**非红（ADR-0003）。

## 7–8. 日志与恢复
[Camera_Error_Recovery.md](../06_Error_Recovery/Camera_Error_Recovery.md)
