# Release_035 验收报告

## 执行时间

2026-07-02 01:59:42 UTC

## 执行命令

```bash
python scripts/verify_release_035.py
python scripts/verify_all.py --only 035
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall` (0.36s)
- [PASS] `runtime_isolation` (0.11s) — runtime/verification/R035/workspace_state_mock.json
- [PASS] `mainwindow_boot` (0.94s)
- [PASS] `current_project_init` (0.64s) — iPhone16_Mainboard
- [PASS] `project_switch_scan_sync` (0.93s)
- [PASS] `project_a_scan_result_path` (5.73s) — runtime/verification/R035/mock_projects/iPhone16_Mainboard/scans/ST-81CB94
- [PASS] `project_b_scan_result_path` (6.77s) — runtime/verification/R035/mock_projects/RF_Module_Test/scans/ST-C7BC54
- [PASS] `scantask_config_project_binding` (0.00s) — A=iPhone16_Mainboard/CPU_Area B=RF_Module_Test/RF_Area
- [PASS] `analysis_data_source_project_isolation` (0.04s)
- [PASS] `report_data_source_project_isolation` (0.05s)
- [PASS] `workspace_project_restore` (0.03s) — runtime/verification/R035/workspace_state_mock.json
- [PASS] `page_switch_regression` (2.08s)
- [PASS] `no_real_device_access` (0.02s)
- [PASS] `no_high_fidelity_changes` (0.06s)

## 结果

PASS

## runtime 隔离路径

- `runtime/verification/R035/`

## 项目 A 扫描结果路径

- `runtime/verification/R035/mock_projects/iPhone16_Mainboard/scans/ST-81CB94`

## 项目 B 扫描结果路径

- `runtime/verification/R035/mock_projects/RF_Module_Test/scans/ST-C7BC54`

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
