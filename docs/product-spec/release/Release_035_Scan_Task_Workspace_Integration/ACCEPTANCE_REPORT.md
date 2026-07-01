# Release_035 验收报告

## 执行时间

2026-07-01 23:47:46 UTC

## 执行命令

```bash
python scripts/verify_release_035.py
python scripts/verify_all.py --only 035
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall` (0.39s)
- [PASS] `runtime_isolation` (0.10s) — runtime/verification/R035/workspace_state_mock.json
- [PASS] `mainwindow_boot` (0.53s)
- [PASS] `current_project_init` (0.50s) — iPhone16_Mainboard
- [PASS] `project_switch_scan_sync` (0.97s)
- [PASS] `project_a_scan_result_path` (5.98s) — runtime/verification/R035/mock_projects/iPhone16_Mainboard/scans/ST-650C5C
- [PASS] `project_b_scan_result_path` (10.14s) — runtime/verification/R035/mock_projects/RF_Module_Test/scans/ST-1034D5
- [PASS] `scantask_config_project_binding` (0.00s) — A=iPhone16_Mainboard/CPU_Area B=RF_Module_Test/RF_Area
- [PASS] `analysis_data_source_project_isolation` (0.06s)
- [PASS] `report_data_source_project_isolation` (0.07s)
- [PASS] `workspace_project_restore` (0.04s) — runtime/verification/R035/workspace_state_mock.json
- [PASS] `page_switch_regression` (2.27s)
- [PASS] `no_real_device_access` (0.03s)
- [PASS] `no_high_fidelity_changes` (0.10s)

## 结果

PASS

## runtime 隔离路径

- `runtime/verification/R035/`

## 项目 A 扫描结果路径

- `runtime/verification/R035/mock_projects/iPhone16_Mainboard/scans/ST-650C5C`

## 项目 B 扫描结果路径

- `runtime/verification/R035/mock_projects/RF_Module_Test/scans/ST-1034D5`

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
