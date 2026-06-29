# Analysis — 分析结果

## 1. 对象定义
基于 ScanTask/Heatmap 的 **可重复生成** 的分析记录，不修改原始数据。

## 2. 为什么需要
Hx/Hy/Total 对比、频点视图、用户结论、报告输入。

## 3. 关键字段
analysisId, regionId, scanTaskIds[], type, parameters, heatmapRef, conclusion, reviewedAt。

## 4. 所属关系
属于 Region；引用 ScanTask。

## 5. 与其它对象关系
1:N Report；依赖 Alignment 决定能否叠加 PCB。

## 6. 生命周期
Created → Configured → Generated → Reviewed → Exported。

## 7. 状态
见 [Analysis_State_Machine.md](../04_State_Machines/Analysis_State_Machine.md)。

## 8. 文件系统映射
`{region}/analysis/{analysisId}.json`

## 9. UI 映射
分析页、navAnalysisButton。

## 10. Qt/PySide6 实现建议
AnalysisService.regenerate() 幂等。

## 11. 禁止事项
禁止 Analysis 写 raw；禁止 Analysis 控设备。

## 相关
[../../data/Analysis.md](../../data/Analysis.md)
