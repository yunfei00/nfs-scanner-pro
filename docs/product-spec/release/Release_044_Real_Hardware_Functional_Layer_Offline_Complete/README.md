# Release 044 — Real Hardware Functional Layer Offline Complete

## 1. Release 目标

在没有真实硬件的情况下，完成运动 / 频谱 / 相机 / 舵机 / 扫描执行器的**完整功能层骨架**，支持 FakeTransport、DryRun 与 CLI 调试入口。

## 2. 为什么没有真实硬件也要先完成

后续接设备时只需调端口、IP、命令差异与返回格式，不必再重构架构。

## 3. 安全开关总表

| 环境变量 | 作用 |
|----------|------|
| `NFS_ENABLE_REAL_HARDWARE=1` | 允许真实连接 |
| `NFS_ENABLE_REAL_MOTION_JOG=1` | 允许 jog |
| `NFS_ENABLE_REAL_MOTION_MOVE=1` | 允许 move_to |
| `NFS_ENABLE_REAL_MOTION_HOME=1` | 允许 home |
| `NFS_ENABLE_REAL_MOTION_ESTOP=1` | 允许急停 |
| `NFS_ENABLE_REAL_SPECTRUM_WRITE=1` | 允许 SCPI 写 |
| `NFS_ENABLE_REAL_SPECTRUM_SWEEP=1` | 允许 sweep |
| `NFS_ENABLE_REAL_SPECTRUM_TRACE_READ=1` | 允许 Trace 读取 |
| `NFS_ENABLE_REAL_CAMERA=1` | 允许相机 |
| `NFS_ENABLE_REAL_SERVO=1` | 允许舵机 |
| `NFS_ENABLE_REAL_SCAN_EXECUTION=1` | 允许 real-run 扫描 |

默认全部为 **False**。

## 4. Transport 架构

`SerialTransport` / `SocketScpiTransport` / `VisaScpiTransport` + `Fake*` 系列。

## 5–8. Adapter 完整接口

见 `MotionGrblAdapter`、`SpectrumScpiAdapter`、`CameraAdapter`、`ServoAdapter`。

## 9. RealDeviceManager

`enable_fake_transports()`、`run_motion_*`、`run_spectrum_*`、`run_scan_offline_or_real()`。

## 10. RealScanExecutor

- `dry_run()` — 只验证计划
- `fake_run()` — FakeTransport 逐点 fake 扫描
- `real_run()` — 强开关，默认 blocked

## 11. CLI 调试脚本

```bash
python scripts/debug_real_motion.py --status --fake
python scripts/debug_real_spectrum.py --idn --fake
python scripts/debug_real_camera.py --capture --fake
python scripts/debug_real_servo.py --state --fake
python scripts/run_real_scan_offline.py --fake-run
```

## 12. 真实设备接入后的调试顺序

1. 运动 connect + status  
2. 频谱 *IDN? + marker  
3. 相机 enumerate + capture  
4. 舵机 state + Hx/Hy  
5. fake-run 扫描  
6. 逐项开启 NFS_ENABLE_REAL_* 做 real-run

## 13. 本次不保证现场联调成功

仅保证代码结构完整、fake 测试通过、默认安全。

## 14. 后续 Release_045 建议

真实硬件接入调试指南 + UI 设备页 Real/Mock 模式切换。
