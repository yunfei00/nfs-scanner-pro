# Release_036 验收报告

## 执行时间

2026-06-30 23:08:42 UTC

## 执行命令

```bash
python scripts/verify_release_036.py
python scripts/verify_all.py --only 036
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall` (0.39s)
- [PASS] `runtime_isolation` (0.10s) — runtime/verification/R036/workspace_state_mock.json
- [PASS] `prepare_multi_project_scan_tasks` (0.02s) — A=['ST-R036-A-001', 'ST-R036-A-002'] B=['ST-R036-B-001']
- [PASS] `mainwindow_boot` (0.50s)
- [PASS] `analysis_data_source_project_isolation` (0.04s)
- [PASS] `analysis_default_load_current_project` (0.55s) — default latest ST-R036-A-002
- [PASS] `scantask_dropdown_switching` (0.63s) — ST-R036-A-001->ST-R036-A-002
- [PASS] `project_switch_analysis_refresh` (0.59s)
- [PASS] `cursor_readout_dataset_binding` (0.81s)
- [PASS] `empty_project_state` (0.58s) — Empty_Project_For_R036
- [PASS] `trace_frequency_lut_controls` (0.69s)
- [PASS] `page_switch_regression` (1.07s)
- [PASS] `workspace_state_saved` (0.01s) — runtime/verification/R036/workspace_state_mock.json
- [PASS] `no_real_device_access` (0.01s)
- [PASS] `no_high_fidelity_changes` (0.06s)

## 结果

PASS

## runtime 隔离路径

- `runtime/verification/R036/`

## 项目 A ScanTask 列表

- `ST-R036-A-001`
- `ST-R036-A-002`

## 项目 B ScanTask 列表

- `ST-R036-B-001`

## 空项目状态

- `Empty_Project_For_R036` — 分析页空状态通过

## workspace_state_mock.json 路径

- `runtime/verification/R036/workspace_state_mock.json`

## 默认 ScanTask 说明

default latest ST-R036-A-002

## 是否接真实设备

否

## 是否实现真实分析算法

否

## 是否生成真实 PDF / Word / Excel

否

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是
