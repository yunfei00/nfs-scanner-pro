# Release_040 验收报告

## 执行时间

2026-07-02 00:54:29 UTC

## 执行命令

```bash
python scripts/verify_release_040.py
python scripts/verify_all.py --only 040
python scripts/check_spectrum_single_point_safe.py
python scripts/check_real_devices_safe.py
```

## 检查项

- [PASS] `compileall` (0.92s)
- [PASS] `real_spectrum_imports` (0.00s)
- [PASS] `default_real_hardware_disabled` (0.00s)
- [PASS] `amplitude_response_parser` (0.00s)
- [PASS] `marker_response_parser` (0.00s)
- [PASS] `scpi_marker_query_whitelist` (0.00s)
- [PASS] `no_connection_when_disabled` (0.00s)
- [PASS] `real_device_manager_single_point_status` (0.00s)
- [PASS] `check_spectrum_single_point_safe_default` (0.86s)
- [PASS] `mock_ui_unchanged` (23.16s)
- [PASS] `source_scpi_command_safety` (0.00s)
- [PASS] `no_high_fidelity_changes` (0.10s)

## 结果

PASS

## 默认是否连接真实设备

否

## 是否修改仪表配置

否

## 是否启动 sweep

否

## 是否读取完整 Trace

否

## 是否支持 Marker 单点幅度读取

是（仅 NFS_ENABLE_REAL_HARDWARE=1）

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是
