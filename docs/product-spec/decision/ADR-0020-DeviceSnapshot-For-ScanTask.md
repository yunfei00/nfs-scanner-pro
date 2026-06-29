# ADR-0020 DeviceSnapshot For ScanTask

## 背景
设备改端口/频点后，历史扫描无法复现；报告需证明「扫描当时」配置。

## 决策
1. 每条 **ScanTask** 在 **ScanStarted**（准备就绪→扫描中）时创建并绑定 **DeviceSnapshot**。
2. Snapshot 含 Motion/Spectrum/Camera/Servo 配置 + 应用版本 + 时间戳。
3. **Analysis 与 Report 必须引用** scanTask.deviceSnapshotId 展示/审计。
4. **当前设备配置变更不影响**已锁定 Snapshot；Profile 变更不 retroactive。
5. Scan 完成后 Snapshot **locked**。

## 后果
- 磁盘略增；可追溯性满足 EMC 实验室要求。

## 替代方案
- 仅 Project 级 Snapshot：否决，长项目设备会变。
- 实时读当前配置写报告：否决，不可审计。

## 与已有 Release 关系
- ADR-0006 Device Profile、0007 Scan Record
- domain ScanTask_Lifecycle「冻结设备快照」步骤

## 相关
[DeviceSnapshot.md](../domain/03_Device_Objects/DeviceSnapshot.md)
