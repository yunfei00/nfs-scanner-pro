# Release_041 验收报告

## 执行时间

2026-07-02 02:39:44 UTC

## 执行命令

```bash
python scripts/verify_release_041.py
python scripts/verify_all.py --only 041
python scripts/check_joint_single_point_sample_safe.py
python scripts/check_real_devices_safe.py
```

## 检查项

- [PASS] `compileall` (0.27s)
- [PASS] `joint_sample_imports` (0.00s)
- [PASS] `default_real_hardware_disabled` (0.00s)
- [PASS] `sample_record_builder` (0.00s)
- [PASS] `sample_json_csv_persistence` (0.03s) — runtime/verification/R041/joint_samples/SP-0CD3522D/single_point_sample.json
- [PASS] `no_connection_when_disabled` (0.00s)
- [PASS] `fake_adapter_joint_sample` (0.00s)
- [PASS] `real_device_manager_joint_status` (0.00s)
- [PASS] `check_joint_sample_script_default` (0.89s)
- [PASS] `source_no_motion_or_sweep_commands` (0.00s)
- [PASS] `mock_ui_unchanged` (19.44s)
- [PASS] `no_high_fidelity_changes` (0.08s)

## 结果

PASS

## 默认是否连接真实设备

否

## 是否执行真实运动

否

## 是否启动 sweep

否

## 是否读取完整 Trace

否

## 是否支持 JSON / CSV 单点样本保存

是（仅显式 --save 且 NFS_ENABLE_REAL_HARDWARE=1）

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是
