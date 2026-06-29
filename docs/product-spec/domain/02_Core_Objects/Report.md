# Report — 测试报告

## 1. 对象定义
从 Project/Region/ScanTask/Analysis **派生**的正式输出文档。

## 2. 为什么需要
实验室交付、归档、审计；不反写源数据。

## 3. 关键字段
reportId, scope, includedRegions[], includedAnalyses[], format, exportPath, generatedAt, status。

## 4. 所属关系
属于 Project；引用 Analysis。

## 5. 与其它对象关系
Analysis 1:N Report；含 DeviceSnapshot 摘要。

## 6. 生命周期
Draft → Generated → Reviewed → Exported → Archived。

## 7. 状态
见 [Report_State_Machine.md](../04_State_Machines/Report_State_Machine.md)。

## 8. 文件系统映射
`{project}/reports/{reportId}/` + exports/

## 9. UI 映射
报告页 navReportButton、导出 Dialog。

## 10. Qt/PySide6 实现建议
模板引擎 PDF/Word；异步生成 + 进度。

## 11. 禁止事项
禁止 Report 修改 ScanTask raw；禁止 Report 启动扫描。

## 相关
[../../data/Report.md](../../data/Report.md)
