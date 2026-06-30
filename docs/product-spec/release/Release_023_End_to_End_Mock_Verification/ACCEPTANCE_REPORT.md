# Release_023 验收报告

## 执行命令

```bash
python scripts/verify_release_023.py
python scripts/verify_all.py
```

## 验收时间

2026-06-30 14:21:34 UTC

## 检查项

- [PASS] `compileall`
- [PASS] `gitignore` — ok
- [PASS] `mainwindow_single_dock` — count=1
- [PASS] `page_dock_mapping` — 0:'扫描参数', 1:'设备配置', 2:'分析参数', 3:'报告设置'
- [PASS] `project_mock` — recent=3 closed=closed
- [PASS] `workspace_persistence` — file=workspace_state_mock.json gitignored=True
- [PASS] `device_manager_mock`
- [PASS] `scan_engine_mock` — state=已完成 qtimer=False
- [PASS] `scan_result_persistence` — dir=D:\code_2026\nfs-scanner-pro\runtime\mock_projects\iPhone16_Mainboard\scans\ST-VERIFY-023 csv_rows=100
- [PASS] `analysis_data_source` — tasks=['ST-04973B', 'ST-0F358C', 'ST-2F507F', 'ST-33A2D9', 'ST-42B130', 'ST-555F01', 'ST-6EBD6B', 'ST-8A1B9F', 'ST-C6FE67', 'ST-CECCD6', 'ST-CF3710', 'ST-F145AF', 'ST-F15656', 'ST-F8038E', 'ST-VERIFY-001', 'ST-VERIFY-023'] empty_ok=True
- [PASS] `report_data_source` — D:\code_2026\nfs-scanner-pro\runtime\mock_projects\iPhone16_Mainboard\reports\RP-VERIFY-023\report_draft.json
- [PASS] `no_real_device_access`

## 结果

PASS

## runtime Mock 文件

- `runtime/mock_projects/iPhone16_Mainboard/scans/ST-VERIFY-023/`
- `runtime/mock_projects/iPhone16_Mainboard/reports/RP-VERIFY-023/report_draft.json`
- `runtime/workspace_state_mock.json`

## 是否接真实设备

否

## 是否生成真实 PDF / Word / Excel

否

## 是否可以提交

是
