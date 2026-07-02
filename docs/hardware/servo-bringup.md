# 舵机联调清单

## 接口说明

`ServoAdapter`：get_state / switch_hx / switch_hy / calibrate / snapshot。

## 为什么默认不控制舵机

误切换探头可能导致测量错误。需显式 `NFS_ENABLE_REAL_SERVO=1`。

## 状态查询

```powershell
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_ENABLE_REAL_SERVO="1"
python scripts/debug_real_servo.py --state
```

Fake：

```powershell
python scripts/debug_real_servo.py --state --fake
```

## Hx / Hy 切换与校准

需 `NFS_ENABLE_REAL_SERVO=1`，建议先 `--state` 再切换。

## 常见问题

| 现象 | 处理 |
|------|------|
| 端口错误 | 检查 COM 口与 yaml `servo.port` |
| 无响应 | 波特率、协议确认 |
| 角度异常 | 检查 hx_angle / hy_angle 配置 |
