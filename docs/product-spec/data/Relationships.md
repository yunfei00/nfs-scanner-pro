# Relationships

## 总体关系

NFS Scanner Professional 的核心对象关系如下：

```text
System
  Device Profiles
  Projects

Project
  Sample
  Device Snapshot
  Regions
  Reports

Region
  Alignment
  Scan Configuration
  Scans
  Analysis Results
  Exports

Scan
  Device Snapshot
  Raw Data
  Processed Data
```

## Project 与 Region

一个 Project 表示一个 PCB 或一个被测对象。

一个 Project 可以包含多个 Region。

一个 Region 必须属于一个 Project。

## Region 与 Scan

一个 Region 可以包含多次 Scan。

典型情况：

- Scan Hx
- Scan Hy

重新扫描时应创建新的 Scan，而不是覆盖旧 Scan。

## Region 与 Alignment

Alignment 属于 Region。

同一个 Project 的 Sample 图片可以被多个 Region 引用。

每个 Region 保存自己的图像区域和坐标映射。

## Device Profile 与 Device Snapshot

Device Profile 是系统级模板。

Device Snapshot 是 Project 或 Scan 中保存的快照。

历史 Project 不应因为 Device Profile 修改而变化。

## Analysis 与 Report

Analysis 基于 Scan 数据生成。

Report 引用 Project、Region、Scan、Analysis 的结果生成。

Report 不修改原始数据。
