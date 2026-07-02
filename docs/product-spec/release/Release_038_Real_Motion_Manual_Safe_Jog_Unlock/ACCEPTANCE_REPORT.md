# Release_038 验收报告

## 执行时间

2026-07-02 00:54:29 UTC

## 执行命令

```bash
python scripts/verify_release_038.py
python scripts/verify_all.py --only 038
python scripts/verify_all.py --from 037
python scripts/verify_all.py
python scripts/manual_motion_jog_safe.py --axis x --direction + --step 0.1 --dry-run
python scripts/check_real_devices_safe.py
```

## 检查项

- [PASS] `compileall` (0.51s)
- [PASS] `real_motion_imports` (0.00s)
- [PASS] `default_jog_disabled` (0.00s)
- [PASS] `jog_command_builder` (0.00s)
- [PASS] `soft_limit_validation` (0.00s)
- [PASS] `dry_run_no_motion` (0.00s) — $J=G91 G21 X0.100 F100
- [PASS] `jog_requires_double_enable` (0.00s)
- [PASS] `manual_jog_script_default_safe` (1.52s)
- [PASS] `source_motion_command_safety` (0.02s)
- [PASS] `mock_ui_unchanged` (8.48s)
- [PASS] `no_high_fidelity_changes` (0.12s)

## 结果

PASS

## 默认是否连接真实设备

否

## 默认是否执行真实点动

否

## 是否需要双重开关

是（NFS_ENABLE_REAL_HARDWARE=1 且 NFS_ENABLE_REAL_MOTION_JOG=1）

## 是否支持 dry-run

是

## 是否执行 home

否

## 是否执行 move_to

否

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是
