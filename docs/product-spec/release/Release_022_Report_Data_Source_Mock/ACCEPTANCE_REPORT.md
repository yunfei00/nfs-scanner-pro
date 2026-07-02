# Release_022 验收报告

## 验收时间

2026-07-02 00:17:25 UTC

## 执行命令

```bash
python scripts/verify_release_022.py
```

## 检查项

- [PASS] `compileall`
- [PASS] `module_imports`
- [PASS] `gitignore_runtime` — ok
- [PASS] `mock_scan_result_ready` — D:\code_2026\nfs-scanner-pro\runtime\verification\R022\mock_projects\iPhone16_Mainboard\scans\ST-VERIFY-001
- [PASS] `analysis_dataset_load` — projects=1 tasks=['ST-VERIFY-001'] empty=False
- [PASS] `analysis_cursor_readout` — keys=['amp', 'frequency', 'phase', 'x', 'y', 'z']
- [PASS] `report_context_build` — default_name='CPU_Area_Hx_2.45GHz_报告' has_data=True
- [PASS] `report_draft_fields` — CPU_Area_Hx_2.45GHz_报告
- [PASS] `report_draft_save` — D:\code_2026\nfs-scanner-pro\runtime\verification\R022\mock_projects\iPhone16_Mainboard\reports\RP-VERIFY-022\report_draft.json
- [PASS] `no_real_export_files` — unexpected=[]
- [PASS] `no_real_device_access`
- [PASS] `mainwindow_single_right_dock` — count=1
- [PASS] `no_project_in_left_nav` — nav=['扫描', '设备', '分析', '报告', '⟩']
- [PASS] `page_dock_mapping` — 0:'扫描参数', 1:'设备配置', 2:'分析参数', 3:'报告设置'
- [PASS] `report_toolbar` — ['新建报告', '预览', '导出 PDF', '导出 Word', '导出 Excel']
- [PASS] `scan_toolbar_restore` — ['开始扫描', '停止扫描', '拍照', '区域对齐', '网格', '测量']

## 结果

PASS

## runtime Mock 文件

- 扫描：`runtime/verification/R022/mock_projects/iPhone16_Mainboard/scans/ST-VERIFY-001/`
- 报告草稿：`D:/code_2026/nfs-scanner-pro/runtime/verification/R022/mock_projects/iPhone16_Mainboard/reports/RP-VERIFY-022/report_draft.json`

## 是否生成真实 PDF / Word / Excel

否

## 是否接真实设备

否

## 是否可以提交

是
