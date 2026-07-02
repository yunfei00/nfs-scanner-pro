# Release_043 验收报告

## 执行时间

2026-07-02 01:20:45 UTC

## 执行命令

```bash
python scripts/verify_release_043.py
python scripts/verify_all.py --only 043
python scripts/manual_3x3_point_sample_safe.py
```

## 检查项

- [PASS] `compileall` (0.11s)
- [PASS] `manual_scan_imports` (0.00s)
- [PASS] `create_manual_session` (0.00s)
- [PASS] `position_tolerance_validation` (0.00s)
- [PASS] `fake_sample_update` (0.00s)
- [PASS] `manual_session_persistence` (0.04s) — runtime/verification/R043/manual_scan_sessions/MS-16EF5109/manual_scan_session.json
- [PASS] `script_default_safe` (0.95s)
- [PASS] `script_create_session` (1.46s)
- [PASS] `script_fake_sample` (1.10s)
- [PASS] `script_requires_confirm_for_real_sample` (0.99s)
- [PASS] `source_no_motion_or_sweep_commands` (0.00s)
- [PASS] `mock_ui_unchanged` (46.88s)
- [PASS] `no_high_fidelity_changes` (0.10s)

## 结果

PASS

## 是否默认连接真实设备

否

## 是否执行真实运动

否

## 是否自动采 9 个点

否

## 是否启动 sweep

否

## 是否支持 fake sample

是

## 是否支持 session 断点

是

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是
