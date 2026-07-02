# 硬件调试总入口

nfs-scanner-pro 真实硬件层已离线实现完毕。本目录为 **接设备前 / 接设备后** 的联调准备文档。

## 当前支持设备

| 设备 | Adapter | CLI |
|------|---------|-----|
| 运动平台 (GRBL) | `MotionGrblAdapter` | `debug_real_motion.py` |
| 频谱仪 (SCPI) | `SpectrumScpiAdapter` | `debug_real_spectrum.py` |
| 相机 | `CameraAdapter` | `debug_real_camera.py` |
| 舵机 Hx/Hy | `ServoAdapter` | `debug_real_servo.py` |
| 联合扫描 | `RealScanExecutor` | `run_real_scan_offline.py` |

## Mock / Fake / Real 对照

| 模式 | 连接真实设备 | 典型用途 |
|------|--------------|----------|
| **Mock** | 否 | UI 原型、Mock 扫描 |
| **Fake / DryRun** | 否（FakeTransport） | 命令链路、计划、结果格式验证 |
| **Real** | 是（需全部安全开关） | 现场联调 |

环境变量：`NFS_HARDWARE_MODE=mock|fake|real`

## 调试顺序（推荐）

1. 运行接口审计：`python scripts/check_hardware_interface_inventory.py`
2. 生成诊断报告：`python scripts/generate_hardware_bringup_report.py`
3. 复制 `config/hardware.local.example.yaml` → `config/hardware.local.yaml`
4. 不接设备：fake 命令与 UI fake-run
5. 逐项接设备：运动 status → 频谱 IDN → 相机 list → 舵机 state
6. UI 真实扫描控制台：dry-run → fake-run
7. 全部子开关确认后再 real-run

## 不接设备时可以做什么

- 接口完整性审计
- 硬件联调诊断报告（离线）
- FakeTransport 调试（`--fake` / `--fake-run`）
- UI Mock / Fake 模式切换
- 真实扫描控制台 dry-run / fake-run

## 接设备后怎么做

见各设备 bring-up 文档与安全开关文档。首次联调 **只读、不运动、不 sweep**。

## 安全开关总览

见 [hardware-safety-switches.md](hardware-safety-switches.md)

## 相关文档

- [motion-platform-bringup.md](motion-platform-bringup.md)
- [spectrum-analyzer-bringup.md](spectrum-analyzer-bringup.md)
- [camera-bringup.md](camera-bringup.md)
- [servo-bringup.md](servo-bringup.md)
- [real-scan-bringup.md](real-scan-bringup.md)
- [hardware-debug-command-map.md](hardware-debug-command-map.md)
- [hardware-troubleshooting.md](hardware-troubleshooting.md)
- [../hardware-debug-guide.md](../hardware-debug-guide.md)
