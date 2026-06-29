# 分析页 — 设计说明（占位）

## 1. 页面目标

对比频率数据、查看统计结果、关联 ScanTask 与 Heatmap。

## 2. 使用场景

扫描完成后进入 **分析** 页查看曲线与表格。

## 3. 页面结构（规划）

左侧结果列表 + 中央图表区 + 可选参数 Dock。

## 4. 显示内容

Analysis 结果列表、频率对比 Mock。

## 5. 默认隐藏

频谱 Dock 默认隐藏，分析页内嵌主图表区。

## 6. 与 Dock

统计面板经视图菜单，非默认。

## 7. 与菜单栏

**分析** 菜单导出、对比操作。

## 8. 领域对象

Analysis、FrequencyData、ScanTask（只读）。

## 9. PySide6 建议

`analysisPage` 占位 → Release 012+ 细化。

## 10. 高保真

本 Release 仅占位说明，完整高保真后续 Release。
