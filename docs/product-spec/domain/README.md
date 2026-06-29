# Enterprise Domain Model — 领域模型总览

> **Release 009.8** · 产品领域对象、状态机、生命周期与异常恢复的权威入口。

## 快速入口

| 入口 | 链接 |
|---|---|
| **对象关系（含文字说明）** | [01_Overview/Object_Relationships.md](01_Overview/Object_Relationships.md) |
| **状态机** | [04_State_Machines/README.md](04_State_Machines/README.md) |
| **Scan 状态机（详细）** | [04_State_Machines/Scan_State_Machine.md](04_State_Machines/Scan_State_Machine.md) |
| **生命周期** | [05_Lifecycle/ScanTask_Lifecycle.md](05_Lifecycle/ScanTask_Lifecycle.md) |
| **异常恢复** | [06_Error_Recovery/README.md](06_Error_Recovery/README.md) |
| **UI 映射** | [07_Implementation_Guide/Domain_To_UI_Mapping.md](07_Implementation_Guide/Domain_To_UI_Mapping.md) |
| **文件映射** | [07_Implementation_Guide/Domain_To_File_System_Mapping.md](07_Implementation_Guide/Domain_To_File_System_Mapping.md) |
| **领域事件** | [07_Implementation_Guide/Domain_Event_Model.md](07_Implementation_Guide/Domain_Event_Model.md) |

## 与 `data/` 的关系

| 目录 | 角色 |
|---|---|
| `data/` | 首版（**保留**） |
| `domain/` | **当前权威** |

`Sample→PCB`，`Scan→ScanTask`。

## 目录索引

| 层 | 路径 |
|---|---|
| 概览 | [01_Overview/](01_Overview/Domain_Principles.md) |
| 核心对象 | [02_Core_Objects/](02_Core_Objects/Project.md) |
| 设备对象 | [03_Device_Objects/](03_Device_Objects/MotionSystem.md) |
| 状态机 | [04_State_Machines/](04_State_Machines/README.md) |
| 生命周期 | [05_Lifecycle/](05_Lifecycle/Project_Lifecycle.md) |
| 异常恢复 | [06_Error_Recovery/](06_Error_Recovery/README.md) |
| 实现映射 | [07_Implementation_Guide/](07_Implementation_Guide/README.md) |

## 领域原则（10 条）

见 [Domain_Principles.md](01_Overview/Domain_Principles.md)

## Release 与 ADR

- [Release 009.8 README](../release/Release_009_8_Enterprise_Domain_Model/README.md)
- [Release 009.5 UI Foundation](../release/Release_009_5_Enterprise_UI_Foundation/README.md)
- ADR：[0015](../decision/ADR-0015-Enterprise-Domain-Model.md) · [0016](../decision/ADR-0016-Enterprise-Domain-Model.md) · [0017](../decision/ADR-0017-Scan-State-Machine.md) · [0018](../decision/ADR-0018-Project-As-Folder-Domain.md) · [0019](../decision/ADR-0019-Region-Alignment-Ownership.md) · [0020](../decision/ADR-0020-DeviceSnapshot-For-ScanTask.md)
