# Report

## 定义

Report 表示从 Project、Region、Scan 和 Analysis 数据生成的正式输出。

## 职责

Report 负责组织：

- 项目信息
- 样品信息
- 设备快照
- Region 信息
- 扫描参数
- 热力图
- 分析结果
- 结论
- 导出记录

## 报告范围

Report 可以包含：

- 单个 Region
- 多个 Region
- 整个 Project

## 导出格式

第一版支持：

- PDF
- Word
- Excel
- 图片

## 规则

- Report 从保存的数据生成。
- Report 不直接控制设备。
- Report 不修改原始 Scan 数据。
- Report 应保存导出历史。

## 生命周期

- Draft
- Generated
- Reviewed
- Exported
- Archived
