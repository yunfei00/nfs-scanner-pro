# Release 046 — Real Scan UI Console Dry Fake Real Entry

## 1. Release 目标

在 Release_044 / Release_045 真实硬件功能层与硬件模式切换基础上，于扫描页右侧 **扫描参数** Dock 内增加 **真实扫描控制台**，提供 dry-run / fake-run / real-run 三种执行入口（real-run 默认 blocked）。

## 2. 为什么需要真实扫描 UI 控制台

- 将 `RealScanExecutor` 能力暴露给 UI，便于离线验证计划与结果
- 用户可在接设备前熟悉 dry-run → fake-run → real-run 流程
- 与 Mock 扫描按钮并存，不破坏现有原型

## 3. Dry Run 说明

- 仅校验 `scan_plan`，不连接设备
- 不写真实采样，生成空点结果与 summary

## 4. Fake Run 说明

- 使用 `FakeTransport` 执行 9 点 fake 扫描
- 保存 `scan_result.json` / `scan_points.csv` / `scan_summary.json` / `scan_log.jsonl`
- `real_hardware=false`，`motion_command_executed=fake`

## 5. Real Run 说明

- UI 提供入口，默认 **禁用 / blocked**
- 需 `NFS_HARDWARE_MODE=real` + `NFS_ENABLE_REAL_HARDWARE=1` + `NFS_ENABLE_REAL_SCAN_EXECUTION=1`
- 本 Release 不执行真实 real-run（仍返回 blocked 说明）

## 6. 为什么 Real Run 默认禁用

防止误触导致真实运动、sweep 或 trace 读取。接设备后由用户逐项开启安全开关再调试。

## 7. UI 控件说明

位于扫描页右侧 Dock「真实扫描控制台」分组：

- 硬件模式显示
- 计划路径 / 加载 / 默认 3x3
- 计划摘要
- 执行模式：Dry / Fake / Real
- 验证、执行、暂停、恢复、停止
- 进度条与日志
- 输出文件路径

## 8. RealScanConsoleModel

纯数据模型（无 Qt、无设备）：`hardware_mode`、`plan_summary`、`execution_mode`、`progress`、`logs`、`output_paths`、`real_run_enabled`。

## 9. RealScanConsoleController

加载计划、调用 `RealScanExecutor.dry_run/fake_run/real_run`，维护 Model，默认不连接真实设备。

## 10. RealScanExecutor 关系

Controller 委托 Executor 执行；UI 不直接构造 G-code 或 SCPI。

## 11. 输出文件格式

与 Release_044 一致，写入 `runtime/real_scan_runs/{task_id}/`（验收隔离至 `runtime/verification/R046/`）。

## 12. 安全开关说明

见 Release_045 `docs/hardware-debug-guide.md`；Real Run 额外需要 `NFS_ENABLE_REAL_SCAN_EXECUTION=1`。

## 13. 本次不做什么

- ❌ 不默认连接真实设备 / 不运动 / 不 sweep / 不读真实 trace
- ❌ 不在验收中执行 real-run
- ❌ 不改 high_fidelity / 左侧导航 / 菜单栏

## 14. 下一步 Release_047 建议

**真实扫描控制台日志、异常与断点续扫增强** — 结构化日志级别、失败点重试、会话恢复。

## 验收

```bash
python scripts/verify_release_046.py
python scripts/verify_all.py --only 046
```
