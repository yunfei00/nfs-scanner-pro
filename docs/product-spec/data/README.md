# Data Model

本目录定义 NFS Scanner Professional 的产品数据模型。

这里描述的是产品领域对象，不是数据库表，也不是代码类。

## 核心对象

- Project：一个 PCB 或一个被测对象。
- Sample：项目中的被测样品信息。
- Region：PCB 上的一个扫描区域。
- Scan：Region 下的一次采集任务。
- Alignment：Region 与样品图像、运动坐标之间的对应关系。
- Device Profile：系统级可复用设备配置。
- Device Snapshot：项目或扫描时保存的设备快照。
- Analysis：基于扫描数据产生的分析结果。
- Report：基于项目和分析结果生成的报告。

## 基本关系

Project 是最高容器。

一个 Project 包含一个 Sample，可以包含多个 Region。

一个 Region 可以包含多次 Scan，例如 Hx Scan 和 Hy Scan。

Alignment 属于 Region。

Device Profile 属于系统，Device Snapshot 属于 Project 或 Scan。
