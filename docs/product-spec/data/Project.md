# Project

## 定义

Project 表示一个 PCB 或一个被测对象的完整测试工程。

Project 不是一次扫描，也不是一个扫描区域。

Project 是产品数据的最高业务容器。

## 职责

Project 负责组织：

- 样品信息
- 设备快照
- 多个扫描区域 Region
- 扫描数据
- 分析结果
- 报告与导出文件
- 项目日志

## 规则

- 一个 Project 对应一个 PCB 或一个被测对象。
- 一个 Project 可以包含多个 Region。
- 一个 Project 应该可以作为一个文件夹整体移动、备份和归档。
- Project 页面不直接控制设备，也不直接启动扫描。

## 生命周期

- Created：项目已创建。
- Configured：样品和基础配置已完成。
- Active：项目正在使用。
- Completed：主要测试工作完成。
- Archived：项目已归档。

## 必要信息

- Project Name
- Project ID
- Customer
- Sample Name
- Sample ID
- Operator
- Created Time
- Updated Time
- Notes

## 关联对象

- Sample：一对一。
- Region：一对多。
- Device Snapshot：一对一或按扫描记录保存。
- Report：一对多。

## 禁止事项

Project 不应保存临时 UI 状态。

Project 不应替代 Region 保存扫描区域信息。

Project 不应直接保存设备实时连接状态。
