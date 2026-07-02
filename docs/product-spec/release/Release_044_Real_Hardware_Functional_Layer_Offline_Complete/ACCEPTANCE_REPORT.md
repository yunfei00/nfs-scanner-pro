# Release_044 验收报告

## 执行时间

2026-07-02 00:54:30 UTC

## 执行命令

```bash
python scripts/verify_release_044.py
python scripts/verify_all.py --only 044
python scripts/run_real_scan_offline.py --fake-run
python scripts/debug_real_motion.py --fake --status
```

## 检查项

- [PASS] `compileall` (0.64s)
- [PASS] `real_hardware_imports` (0.00s)
- [PASS] `safety_flags_default_false` (0.00s)
- [PASS] `fake_transports` (0.00s)
- [PASS] `motion_full_api_offline` (0.00s)
- [PASS] `spectrum_full_api_offline` (0.00s)
- [PASS] `camera_full_api_offline` (0.00s)
- [PASS] `servo_full_api_offline` (0.00s)
- [PASS] `real_device_manager_offline` (0.00s)
- [PASS] `real_scan_executor_dry_run` (0.01s) — runtime/verification/R044/real_scan_runs/RS-DE5CD4E8/scan_result.json
- [PASS] `real_scan_executor_fake_run` (0.02s) — runtime/verification/R044/real_scan_runs/RS-0CA923DD/scan_result.json
- [PASS] `cli_default_safe` (6.30s)
- [PASS] `cli_fake_mode` (4.02s)
- [PASS] `source_safety_guards` (0.00s)
- [PASS] `mock_ui_unchanged` (86.10s)
- [PASS] `no_high_fidelity_changes` (0.10s)

## 结果

PASS

## runtime 隔离路径

- `runtime/verification/R044/`

## 是否默认连接真实设备

否

## 是否执行真实运动 / sweep

否

## 是否支持 fake transport / fake-run

是

## real-run 是否默认 blocked

是

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是
