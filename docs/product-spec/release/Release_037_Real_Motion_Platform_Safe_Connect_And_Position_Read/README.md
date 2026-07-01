# Release 037 — Real Motion Platform Safe Connect And Position Read

## 1. Release 目标

真实运动平台第一阶段：串口安全连接、GRBL 状态查询（`?`）、MPos/WPos 坐标读取、安全断开。不执行任何运动命令。

## 2. 为什么先做安全连接与位置读取

- Release_036 已建立 Adapter 桥接层，但尚未验证 GRBL 协议解析。
- 在开放 jog/move/home 之前，必须先证明 **能连、能读、能断** 且默认不连接。

## 3. NFS_ENABLE_REAL_HARDWARE 安全开关

```bash
# 默认：不打开串口
# 启用：
$env:NFS_ENABLE_REAL_HARDWARE="1"
```

## 4. NFS_MOTION_PORT / NFS_MOTION_BAUDRATE 配置

| 环境变量 | 默认 |
|---|---|
| `NFS_MOTION_PORT` | COM6 |
| `NFS_MOTION_BAUDRATE` | 115200 |
| `NFS_MOTION_TIMEOUT` | 2.0 |

## 5. MotionGrblAdapter 接口

- `connect()` / `disconnect()` / `is_connected()`
- `query_status()` → 解析 GRBL 状态行
- `refresh_position()` → 优先 MPos，其次 WPos
- `parse_grbl_status_line(line)` → 纯解析，无需串口
- `snapshot()` → 含 `safe_mode: true`

## 6. GRBL 状态解析

示例：`<Idle|MPos:0.000,1.000,2.000|FS:0,0>`

解析字段：`state`, `mpos`, `wpos`, `x`, `y`, `z`, `source`, `raw`, `ok`, `error`

## 7. 本次允许命令

- 串口 `connect` / `disconnect`
- 发送 `?` 查询状态（唯一允许的 write）

## 8. 本次禁止命令

- G0 / G1 / G28 / $H / $J / jog / home / move_to / stop 真实命令
- M114 等其它 G-code
- 真实扫描 / 相机 / 舵机 / 频谱配置变更

## 9. check_real_devices_safe.py 用法

```powershell
# 默认（不连接）
python scripts/check_real_devices_safe.py

# 手动启用后探测
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_MOTION_PORT="COM6"
python scripts/check_real_devices_safe.py
```

## 10. 本地验收方式

```bash
python scripts/verify_release_037.py
python scripts/verify_all.py --only 037
```

## 11. 后续 Release_038 建议

**真实运动平台手动安全点动解锁流程** — 在用户显式确认后，单独解锁 jog（仍禁止 home / 扫描路径）。
