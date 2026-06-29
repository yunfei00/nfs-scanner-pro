# ADR-0015 Enterprise Domain Model

## 状态
Accepted

## 背景
Release 009.5 完成 UI Foundation，但领域对象仍分散于 `data/`、workflow 与 ADR-0001~0010。MainWindow Prototype 需要 Mock 数据、状态机与异常模型统一来源。

## 决策
1. 新增 `docs/product-spec/domain/` 作为 **Release 009.8 权威领域层**。
2. 保留 `data/` 不删除；Sample→**PCB**，Scan→**ScanTask** 命名升级。
3. 引入完整状态机（`04_State_Machines/`）与异常恢复（`06_Error_Recovery/`）。
4. ScanTask 必须绑定 Project+PCB+Region+Probe+DeviceSnapshot。
5. DeviceProfile 系统级；DeviceSnapshot 任务级冻结。
6. 所有状态转换可写 `{project}/logs/`。

## 后果
### 正面
- Release 010 Mock 与 JSON 结构可推导
- UI Interaction 与 Scan 状态机可对齐

### 负面
- `data/` 与 `domain/` 并存，需读 README 辨别优先级
- 命名 Sample/Scan 在旧 workflow 文中仍存在

## 约束
- 不修改 Release 008/009.5 线框与 Design Token
- 不写 PySide6 实现代码于本 ADR
- Region 删除不得静默删 raw ScanTask

## 与既有 ADR 关系
| ADR | 领域体现 |
|---|---|
| 0001 | Project 1:1 PCB |
| 0003 | Camera_Error_Recovery |
| 0004 | Probe/HxHyCalibration |
| 0005 | Alignment 属 Region |
| 0007 | ScanTask 不覆盖 raw |
| 0008 | Domain_To_File_System_Mapping |
| 0010 | Heatmap 对象 |

## 相关
- [Release 009.8 README](../release/Release_009_8_Enterprise_Domain_Model/README.md)
- [domain/README.md](../domain/README.md)
