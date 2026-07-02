# 真实扫描联调清单

## 执行链路

scan_plan → `RealScanExecutor` → Adapter 层 → 结果写入 `runtime/real_scan_runs/`

## scan_plan

- 生成：`generate_3x3_scan_plan()`
- 持久化：`runtime/scan_plans/{plan_id}/scan_plan.json`
- UI：扫描页「真实扫描控制台」

## dry-run

- 仅校验计划，不连接设备
- `python scripts/run_real_scan_offline.py --dry-run`

## fake-run

- FakeTransport，9 点 fake 采样
- `python scripts/run_real_scan_offline.py --fake-run`

## real-run

需同时满足：

- `NFS_HARDWARE_MODE=real`
- `NFS_ENABLE_REAL_HARDWARE=1`
- `NFS_ENABLE_REAL_SCAN_EXECUTION=1`
- 以及 motion move / spectrum trace 或 sweep 等子开关

**默认 blocked**，不在 CI 中执行。

## 真实扫描前检查清单

- [ ] 接口审计 PASS
- [ ] 诊断报告已生成
- [ ] hardware.local.yaml 已配置
- [ ] 运动平台 status 正常
- [ ] 频谱 IDN / marker 正常
- [ ] fake-run 9 点结果正确
- [ ] 急停方案已确认

## 出错如何停止

- UI「停止」：仅请求 executor stop，不发送真实急停
- 真实急停：需 `NFS_ENABLE_REAL_MOTION_ESTOP=1` 单独启用

## 输出文件

| 文件 | 说明 |
|------|------|
| scan_result.json | 完整结果 |
| scan_points.csv | 逐点数据 |
| scan_summary.json | 摘要 |
| scan_log.jsonl | 执行日志 |
