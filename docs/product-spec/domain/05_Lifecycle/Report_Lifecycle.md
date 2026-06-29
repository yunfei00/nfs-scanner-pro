# Report Lifecycle — 报告生命周期

## 生命周期流程

```text
选择扫描结果（ScanTask / Analysis / Region 范围）
  ↓
选择模板（PDF / Word / Excel …）
  ↓
生成报告（异步）
  ↓
预览
  ↓
导出（写入 exports/）
  ↓
归档（Archived）
```

## 各阶段说明

| 阶段 | 状态 | 说明 |
|---|---|---|
| 选择扫描结果 | Draft | 勾选 Region、ScanTask、Analysis |
| 选择模板 | Draft | 模板 ID + 封面/结论字段 |
| 生成报告 | Generating → Generated | 读 DeviceSnapshot 摘要 |
| 预览 | Generated | 报告页内嵌预览 |
| 导出 | Exported | 文件路径写入 report.json |
| 归档 | Archived | 随 Project 只读 |

## 规则

- Report **不修改** ScanTask raw / Analysis 源
- 历史 Report 找不到 raw 时：预览显示「源数据缺失」+ [Data_Error_Recovery.md](../06_Error_Recovery/Data_Error_Recovery.md)

## 相关

- [Report.md](../02_Core_Objects/Report.md)
- [Report_State_Machine.md](../04_State_Machines/Report_State_Machine.md)
