# 硬件调试命令映射

| 脚本 | 默认连接设备 | Fake | Real | 示例 | 输出 |
|------|--------------|------|------|------|------|
| `debug_real_motion.py` | 否 | `--fake` | 需 NFS_ENABLE_REAL_HARDWARE | `python scripts/debug_real_motion.py --status --fake` | 状态 / 坐标 |
| `debug_real_spectrum.py` | 否 | `--fake` | 需 NFS_ENABLE_REAL_HARDWARE | `python scripts/debug_real_spectrum.py --idn --fake` | IDN / marker |
| `debug_real_camera.py` | 否 | `--fake` | 需 NFS_ENABLE_REAL_CAMERA | `python scripts/debug_real_camera.py --list --fake` | 设备列表 |
| `debug_real_servo.py` | 否 | `--fake` | 需 NFS_ENABLE_REAL_SERVO | `python scripts/debug_real_servo.py --state --fake` | 探头状态 |
| `hardware_debug_wizard.py` | 否 | `--fake-check` | `--real-check` | `python scripts/hardware_debug_wizard.py` | 命令清单 |
| `run_real_scan_offline.py` | 否 | `--fake-run` | `--real-run`（blocked） | `python scripts/run_real_scan_offline.py --fake-run` | 扫描结果文件 |
| `generate_hardware_bringup_report.py` | 否 | N/A | N/A | `python scripts/generate_hardware_bringup_report.py` | JSON + MD 报告 |
| `check_hardware_interface_inventory.py` | 否 | N/A | N/A | `python scripts/check_hardware_interface_inventory.py` | 接口清单 |
| `start_hardware_commissioning.py` | 否 | `--mode fake` | `--mode real-safe` | `python scripts/start_hardware_commissioning.py --mode offline` | session 报告 |
| `validate_commissioning_readiness.py` | 否 | N/A | N/A | `python scripts/validate_commissioning_readiness.py` | READINESS PASS/FAIL |
| `generate_commissioning_template.py` | 否 | N/A | N/A | `python scripts/generate_commissioning_template.py` | 联调模板 |

## 向导入口

```powershell
python scripts/hardware_debug_wizard.py
python scripts/hardware_debug_wizard.py --fake-check
```

## 诊断报告

```powershell
python scripts/generate_hardware_bringup_report.py
```

输出：`runtime/hardware_reports/` 或验收环境 `runtime/verification/R047/`
