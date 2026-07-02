# 02 — 运动平台检查

## 步骤

| ID | 模式 | 说明 |
|----|------|------|
| motion_status | fake/real-safe | status / position |
| motion_jog | real + manual | 小步点动 |

## 命令

```powershell
python scripts/debug_real_motion.py --status --fake
$env:NFS_ENABLE_REAL_HARDWARE="1"
python scripts/debug_real_motion.py --status
```

## 风险

jog / move / home 需独立 NFS_ENABLE_REAL_MOTION_* 开关。
