# Camera Error Recovery — 相机异常恢复

> 相机**可选**（ADR-0003）。所有失败 **不阻断** ScanTask。

## 异常场景与处理

| 场景 | 检测 | ScanTask | UI | 日志 |
|---|---|---|---|---|
| **相机未连接** | Disabled/Disconnected | **继续** | 指示**灰**，非红 | INFO `CAMERA_OFFLINE` |
| **相机被系统占用** | open 失败 EBUSY | 继续 | statusBar 黄「相机占用」 | WARN `CAMERA_BUSY` |
| **拍照失败** | capture 超时 | 继续 | 工具栏拍照闪红一次 | WARN `CAMERA_CAPTURE_FAIL` |
| **图像分辨率变化** | 与 pcb.json 不一致 | 继续；Alignment→需重新确认 | 提示更新 PCB 图 | WARN `CAMERA_RES_CHANGED` |
| **可选时继续扫描** | 任意上列 | **不**改 Scan 状态机 | 无 modal 挡扫描 | INFO |

## 降级策略

- 无新 PCB 图：沿用旧图或纯热力图
- Alignment 失效时：普通 Heatmap，Report 注明「无叠加图」

## 禁止

- 相机错误设 ScanTask=Error
- 相机指示用 error 红色（用 idle 灰/警告黄）

## 相关

[Camera_State_Machine.md](../04_State_Machines/Camera_State_Machine.md)
