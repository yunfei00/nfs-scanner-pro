# Release_035 验收报告

## 执行时间

2026-07-02 00:08:28 UTC

## 执行命令

```bash
python scripts/verify_release_035.py
python scripts/verify_all.py --only 035
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall` (0.41s)
- [PASS] `runtime_isolation` (0.15s) — runtime/verification/R035/workspace_state_mock.json
- [PASS] `mainwindow_boot` (0.62s)
- [PASS] `current_project_init` (0.54s) — iPhone16_Mainboard
- [PASS] `project_switch_scan_sync` (0.95s)
- [PASS] `project_a_scan_result_path` (4.68s) — runtime/verification/R035/mock_projects/iPhone16_Mainboard/scans/ST-44E17E
- [PASS] `project_b_scan_result_path` (5.37s) — runtime/verification/R035/mock_projects/RF_Module_Test/scans/ST-95CAE8
- [PASS] `scantask_config_project_binding` (0.00s) — A=iPhone16_Mainboard/CPU_Area B=RF_Module_Test/RF_Area
- [PASS] `analysis_data_source_project_isolation` (0.05s)
- [PASS] `report_data_source_project_isolation` (0.05s)
- [PASS] `workspace_project_restore` (0.02s) — runtime/verification/R035/workspace_state_mock.json
- [PASS] `page_switch_regression` (1.72s)
- [PASS] `no_real_device_access` (0.01s)
- [PASS] `no_high_fidelity_changes` (0.05s)

## 结果

PASS

## runtime 隔离路径

- `runtime/verification/R035/`

## 项目 A 扫描结果路径

- `runtime/verification/R035/mock_projects/iPhone16_Mainboard/scans/ST-44E17E`

## 项目 B 扫描结果路径

- `runtime/verification/R035/mock_projects/RF_Module_Test/scans/ST-95CAE8`

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
