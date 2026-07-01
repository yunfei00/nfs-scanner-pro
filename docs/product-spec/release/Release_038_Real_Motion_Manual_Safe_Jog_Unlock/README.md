# Release 038 — Real Motion Manual Safe Jog Unlock

## 1. Release 目标

在 Release_037 已能安全连接和读取位置的基础上，增加**真实运动平台手动安全点动**能力。每次只允许一次极小步长增量点动，仍禁止自动扫描、回零与路径运动。

## 2. 为什么点动需要双重开关

真实硬件开关（`NFS_ENABLE_REAL_HARDWARE=1`）仅允许连接与读取状态/位置。点动会实际移动机械结构，因此额外要求 `NFS_ENABLE_REAL_MOTION_JOG=1`，避免误触或自动化脚本意外运动。

## 3. 环境变量

| 变量 | 说明 |
|------|------|
| `NFS_ENABLE_REAL_HARDWARE=1` | 允许打开串口、连接 GRBL |
| `NFS_ENABLE_REAL_MOTION_JOG=1` | 允许发送 `$J=G91 G21` 增量点动 |
| `NFS_MOTION_PORT` | 串口，默认 `COM6` |
| `NFS_MOTION_MAX_JOG_STEP_MM` | 单次最大步长，默认 `1.0` mm |
| `NFS_MOTION_DEFAULT_JOG_STEP_MM` | 默认步长，默认 `0.1` mm |
| `NFS_MOTION_JOG_FEED_MM_MIN` | 点动进给，默认 `100` |
| `NFS_MOTION_X/Y/Z_MIN/MAX` | 软限位 |

## 4. 软限位配置（默认）

- X: 0.0 ~ 200.0 mm
- Y: -200.0 ~ 0.0 mm
- Z: 0.0 ~ 50.0 mm

## 5. MotionGrblAdapter 接口

- `safe_jog(axis, direction, step_mm, dry_run=False)` — 安全点动主入口
- `build_jog_command(axis, direction, step_mm)` — 生成 `$J=G91 G21` 命令
- `validate_jog(axis, direction, step_mm, current_position)` — 软限位与步长校验
- `connect` / `disconnect` / `query_status` / `refresh_position` — 与 Release_037 相同

## 6. manual_motion_jog_safe.py 用法

**默认 dry-run 预览（不连接、不运动）：**

```bash
python scripts/manual_motion_jog_safe.py --axis x --direction + --step 0.1 --dry-run
```

**无 `--confirm` 时不执行真实点动：**

```bash
python scripts/manual_motion_jog_safe.py --axis x --direction + --step 0.1
```

**真实点动（需双重开关 + `--confirm`）：**

```powershell
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_ENABLE_REAL_MOTION_JOG="1"
$env:NFS_MOTION_PORT="COM6"
python scripts/manual_motion_jog_safe.py --axis x --direction + --step 0.1 --confirm
```

## 7. check_real_devices_safe.py

默认仍只提示未启用，不连接。启用后仅 connect / 读状态 / 读位置 / disconnect，**不点动**。若检测到 `NFS_ENABLE_REAL_MOTION_JOG=1`，会提示使用 `manual_motion_jog_safe.py`。

## 8. 本次允许命令

- `?` — 状态查询
- `$J=G91 G21 X/Y/Z±step F100` — 单次增量点动（双重开关 + 显式 confirm）

## 9. 本次禁止命令

- `G0` / `G1` — 直线/快速移动
- `$H` / `G28` — 回零
- `move_to` / `home` / 连续点动 / 自动扫描

## 10. 本地验收

```bash
python scripts/verify_release_038.py
python scripts/verify_all.py --only 038
python scripts/verify_all.py --from 037
```

## 11. 后续 Release_039 建议

**真实频谱仪安全连接与 IDN / 频率读取** — 在双重硬件开关策略下，先只读 IDN 与当前频率，不修改仪器配置、不触发扫描。
