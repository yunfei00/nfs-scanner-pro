# Release_028 验收报告

## 执行时间

2026-06-30 15:52:48 UTC

## 执行命令

```bash
python scripts/verify_release_028.py
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall`
- [PASS] `mock_scan_result_ready` — D:\code_2026\nfs-scanner-pro\runtime\verification\R028\mock_projects\iPhone16_Mainboard\scans\ST-VERIFY-028
- [PASS] `mainwindow_boot` — docks=1
- [PASS] `report_navigation` — dock='报告设置' status='状态：报告就绪，已加载 Mock 扫描结果 ST-VERIFY-028'
- [PASS] `report_toolbar` — report=True scan_restore=True
- [PASS] `report_settings_dock` — groups=['模板', '导出', '内容', '高级']
- [PASS] `report_data_source` — tasks=1 name='CPU_Area_Hx_2.45GHz_报告'
- [PASS] `report_list_ui` — items=1
- [PASS] `report_preview_ui` — title='CPU_Area 近场扫描报告' missing=[]
- [PASS] `create_report_draft` — drafts+=1 status='状态：Mock：已创建报告草稿 CPU_Area_Hx_2.45GHz_报告'
- [PASS] `preview_mock_action` — 状态：Mock：报告预览已刷新
- [PASS] `export_mock_actions` — 状态：Mock：PDF 导出完成（未生成真实文件）; 状态：Mock：WORD 导出完成（未生成真实文件）; 状态：Mock：EXCEL 导出完成（未生成真实文件）
- [PASS] `report_settings_interaction` — settings=True draft=True
- [PASS] `page_switch_regression` — 0:'扫描参数', 1:'设备配置', 2:'分析参数', 3:'报告设置', 0:'扫描参数', 3:'报告设置'
- [PASS] `no_real_device_access`

## 结果

PASS

## runtime 产物

- `runtime/verification/R028/mock_projects/iPhone16_Mainboard/scans/ST-VERIFY-028/`
- `runtime/verification/R028/mock_projects/iPhone16_Mainboard/reports/`（report_draft.json）

## 是否接真实设备

否

## 是否生成真实 PDF / Word / Excel

否

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是
