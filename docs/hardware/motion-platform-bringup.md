# 运动平台联调清单

## 接口说明

`MotionGrblAdapter` 提供：connect / disconnect / query_status / refresh_position / safe_jog / move_to / home / emergency_stop / snapshot。

## 端口配置

- 环境变量：`NFS_MOTION_PORT`（默认 COM6）
- YAML：`config/hardware.local.yaml` → `motion.port`
- 模板：`config/hardware.example.yaml`

## 安全开关

| 开关 | 作用 |
|------|------|
| `NFS_ENABLE_REAL_HARDWARE=1` | 总开关 |
| `NFS_ENABLE_REAL_MOTION_JOG=1` | 点动 |
| `NFS_ENABLE_REAL_MOTION_MOVE=1` | 绝对移动 |
| `NFS_ENABLE_REAL_MOTION_HOME=1` | 回零 |
| `NFS_ENABLE_REAL_MOTION_ESTOP=1` | 急停 |

## 只读状态（首次推荐）

```powershell
$env:NFS_HARDWARE_MODE="real"
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_MOTION_PORT="COM6"
python scripts/debug_real_motion.py --status
```

## Jog / Move / Home

需对应子开关。验收与 CI **默认不启用**。

## 急停

`emergency_stop()` 需 `NFS_ENABLE_REAL_MOTION_ESTOP=1`，本 Release 默认 blocked。

## 常见问题

| 现象 | 处理 |
|------|------|
| COM 端口不存在 | 检查设备管理器端口号 |
| pyserial 未安装 | `pip install pyserial` |
| GRBL 无响应 | 检查波特率 115200、线缆、上电 |
| 坐标解析失败 | 查看 snapshot `raw_status` |
| 软限位失败 | 检查 NFS_MOTION_X/Y/Z_MIN/MAX |
