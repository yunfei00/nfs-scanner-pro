# Release_030 验收报告

## 执行时间

2026-07-01 23:25:04 UTC

## 执行命令

```bash
python scripts/verify_release_030.py
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall`
- [PASS] `mainwindow_boot` — docks=1 project=iPhone16_Mainboard
- [PASS] `initial_scan_page` — crumb='iPhone16_Mainboard > CPU_Area > Hx 探头 > 2.450 GHz > 6461 点' status='状态：准备就绪'
- [PASS] `device_mock_ready` — connect='Mock：全部设备已连接'
- [PASS] `scan_ui_workflow` — task=ST-C308AB fallback=False points=6461/6461
- [PASS] `scan_result_files` — dir=D:\code_2026\nfs-scanner-pro\runtime\verification\R030\mock_projects\iPhone16_Mainboard\scans\ST-C308AB csv_rows=200
- [PASS] `analysis_loads_scan_task` — task=ST-C308AB points=6461
- [PASS] `analysis_mock_interactions` — trace=Trace 2 freq=2.450 GHz
- [PASS] `report_creates_draft` — draft=D:\code_2026\nfs-scanner-pro\runtime\verification\R030\mock_projects\iPhone16_Mainboard\reports\RP-42EE1544\report_draft.json name='CPU_Area_Hx_2.45GHz_报告'
- [PASS] `report_export_mock` — 状态：Mock：报告预览已刷新; 状态：Mock：PDF 导出完成（未生成真实文件）; 状态：Mock：WORD 导出完成（未生成真实文件）; 状态：Mock：EXCEL 导出完成（未生成真实文件）
- [PASS] `cross_page_regression` — 0:'扫描参数', 1:'设备配置', 2:'分析参数', 3:'报告设置', 0:'扫描参数', 3:'报告设置', 2:'分析参数', 1:'设备配置', 0:'扫描参数'
- [PASS] `workspace_state_saved` — last_page=scan
- [PASS] `no_real_device_access`

## 结果

PASS

## runtime 扫描结果

- `runtime/verification/R030/mock_projects/iPhone16_Mainboard/scans/ST-C308AB/`

## runtime 报告草稿

- `runtime/verification/R030/mock_projects/iPhone16_Mainboard/reports/RP-42EE1544/report_draft.json`

## 是否接真实设备

否

## 是否实现真实扫描算法

否

## 是否生成真实 PDF / Word / Excel

否

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是
