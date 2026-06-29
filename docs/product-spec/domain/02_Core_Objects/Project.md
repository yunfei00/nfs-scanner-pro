# Project — 工程项目

## 1. 对象定义

Project 表示 **一块 PCB（或被测对象）的完整测试工程**，对应磁盘上一个可移植文件夹，是持久化数据的最高容器。

## 2. 为什么需要这个对象

- 长期追溯、报告、多样本区域组织（ADR-0001）
- 备份/归档/迁移以文件夹为单位（ADR-0008）
- 与 UI 解耦：Project 不是一级导航页（ADR-0013）

## 3. 关键字段

| 字段 | 说明 |
|---|---|
| projectId | UUID |
| name, customer, operator | 元数据 |
| pcbRef | 指向 PCB 对象 |
| deviceProfileIdUsed | 创建时引用的 Profile |
| lifecycleStage | Created…Archived |
| createdAt, updatedAt | |
| notes | |

## 4. 所属关系

- 属于 System（软件实例）
- 包含 1 PCB、N Region、N ScanTask（跨 Region 聚合）

## 5. 与其它对象关系

- 1:1 PCB
- 1:N Region
- 1:N ScanTask（经 Region 归属）
- 0:1 Project 级 DeviceSnapshot（可选）
- 1:N Report

## 6. 生命周期

见 [Project_Lifecycle.md](../05_Lifecycle/Project_Lifecycle.md)。

## 7. 状态

持久化 lifecycleStage；**不保存**设备实时连接态、当前页 UI 状态。

## 8. 文件系统映射

```text
{projectRoot}/
  project.json
  sample/          → PCB 图像与 pcb.json
  devices/         → snapshots
  regions/
  reports/
  exports/
  logs/
```

## 9. UI 映射

- **文件菜单**：新建/打开/保存/关闭/打开文件夹
- Breadcrumb 首段项目名
- 无 `navProjectButton`

## 10. Qt/PySide6 实现建议

- `ProjectService`：open/save/close 文件夹
- Recent projects 列表读 project.json 摘要

## 11. 禁止事项

- 禁止 Project 页直接启动扫描或控设备
- 禁止 Project 内嵌 Region 几何（属 Region）
- 禁止临时 UI 写入 project.json

## 相关

- 历史：[../../data/Project.md](../../data/Project.md)
