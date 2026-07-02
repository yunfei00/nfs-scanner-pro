# 硬件安全开关说明

| 环境变量 | 默认值 | 作用 | 风险 | 对应脚本 | 首次建议 |
|----------|--------|------|------|----------|----------|
| `NFS_HARDWARE_MODE` | mock | 硬件模式意图 mock/fake/real | 低 | 全部 | mock |
| `NFS_ENABLE_REAL_HARDWARE` | 未设置 | 真实设备总开关 | 高 | 全部 debug_* | 否 |
| `NFS_ENABLE_REAL_MOTION_JOG` | 未设置 | GRBL 点动 | 中 | debug_real_motion.py | 否 |
| `NFS_ENABLE_REAL_MOTION_MOVE` | 未设置 | 绝对移动 | 高 | debug_real_motion.py | 否 |
| `NFS_ENABLE_REAL_MOTION_HOME` | 未设置 | 回零 | 高 | debug_real_motion.py | 否 |
| `NFS_ENABLE_REAL_MOTION_ESTOP` | 未设置 | 急停 | 中 | debug_real_motion.py | 否 |
| `NFS_ENABLE_REAL_SPECTRUM_WRITE` | 未设置 | SCPI 写 | 中 | debug_real_spectrum.py | 否 |
| `NFS_ENABLE_REAL_SPECTRUM_SWEEP` | 未设置 | sweep | 中 | debug_real_spectrum.py | 否 |
| `NFS_ENABLE_REAL_SPECTRUM_TRACE_READ` | 未设置 | trace 读取 | 低 | debug_real_spectrum.py | 否 |
| `NFS_ENABLE_REAL_CAMERA` | 未设置 | 打开相机 | 低 | debug_real_camera.py | 否 |
| `NFS_ENABLE_REAL_SERVO` | 未设置 | 舵机控制 | 中 | debug_real_servo.py | 否 |
| `NFS_ENABLE_REAL_SCAN_EXECUTION` | 未设置 | 真实扫描执行 | 高 | run_real_scan_offline.py | 否 |

## 优先级

环境变量 > `config/hardware.local.yaml` > 默认值

## 首次联调建议

1. 仅 `NFS_ENABLE_REAL_HARDWARE=1` + 只读命令（status / IDN / list / state）
2. 确认 fake-run PASS 后再逐项开启子开关
3. real-run 为最后一步
