# Release_035 验收报告

## 执行时间

2026-07-01 23:34:58 UTC

## 执行命令

```bash
python scripts/verify_release_035.py
python scripts/verify_all.py --only 035
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall` (0.50s)
- [PASS] `runtime_isolation` (0.13s) — runtime/verification/R035/workspace_state_mock.json
- [PASS] `mainwindow_boot` (0.74s)
- [PASS] `current_project_init` (0.55s) — iPhone16_Mainboard
- [PASS] `project_switch_scan_sync` (1.19s)
- [PASS] `project_a_scan_result_path` (9.68s) — runtime/verification/R035/mock_projects/iPhone16_Mainboard/scans/ST-AC4C09
- [PASS] `project_b_scan_result_path` (7.04s) — runtime/verification/R035/mock_projects/RF_Module_Test/scans/ST-7243F2
- [PASS] `scantask_config_project_binding` (0.00s) — A=iPhone16_Mainboard/CPU_Area B=RF_Module_Test/RF_Area
- [PASS] `analysis_data_source_project_isolation` (0.07s)
- [PASS] `report_data_source_project_isolation` (0.07s)
- [PASS] `workspace_project_restore` (0.03s) — runtime/verification/R035/workspace_state_mock.json
- [PASS] `page_switch_regression` (2.08s)
- [PASS] `no_real_device_access` (0.02s)
- [PASS] `no_high_fidelity_changes` (0.20s)

## 结果

PASS

## runtime 隔离路径

- `runtime/verification/R035/`

## 项目 A 扫描结果路径

- `runtime/verification/R035/mock_projects/iPhone16_Mainboard/scans/ST-AC4C09`

## 项目 B 扫描结果路径

- `runtime/verification/R035/mock_projects/RF_Module_Test/scans/ST-7243F2`

## workspace_state_mock.json 路径

- `runtime/verification/R035/workspace_state_mock.json`

## 是否接真实设备

否

## 是否生成真实 PDF / Word / Excel

否

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是
