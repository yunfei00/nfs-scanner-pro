# Release_027 验收报告

## 执行时间

2026-07-02 02:29:43 UTC

## 执行命令

```bash
python scripts/verify_release_027.py
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall`
- [PASS] `mock_scan_result_ready` — D:\code_2026\nfs-scanner-pro\runtime\verification\R027\mock_projects\iPhone16_Mainboard\scans\ST-VERIFY-027
- [PASS] `mainwindow_boot` — docks=1
- [PASS] `analysis_navigation` — dock='分析参数' status='状态：分析就绪，已加载 Mock 扫描结果 ST-VERIFY-027'
- [PASS] `analysis_dock_content` — groups=['数据源', '显示设置', '光标', '导出', '高级']
- [PASS] `analysis_data_source` — tasks=1 status='状态：分析就绪，已加载 Mock 扫描结果 ST-VERIFY-027'
- [PASS] `trace_frequency_lut_controls` — trace=Trace 2 freq=2.450 GHz updates=5
- [PASS] `cursor_readout` — x=45.20 mm lock='状态：Mock：光标已锁定'
- [PASS] `export_mock_actions` — 状态：Mock：已导出热力图图片; 状态：Mock：已导出当前读数; 状态：Mock：分析快照已保存
- [PASS] `analysis_canvas_state` — heatmap_opacity=0.67 empty_ok=True
- [PASS] `page_switch_regression` — 0:'扫描参数', 1:'设备配置', 2:'分析参数', 3:'报告设置', 2:'分析参数'
- [PASS] `no_real_device_access`

## 结果

PASS

## runtime 产物

- `runtime/verification/R027/mock_projects/iPhone16_Mainboard/scans/ST-VERIFY-027/`

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
