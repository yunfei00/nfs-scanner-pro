# DeviceSnapshot — 设备快照

## 1. 对象定义
某时刻设备配置与状态 **冻结记录**，用于追溯（ADR-0006/0007）。

## 2. 为什么需要
ScanTask 复现；Report 审计；与 DeviceProfile 解耦。

## 3. 关键字段
snapshotId, sourceProfileId, motion, spectrum, camera, servo, appVersion, createdAt, locked。

## 4. 所属关系
Project 级可选 + **每条 ScanTask 1 个**任务级（推荐）。

## 5. 关系
模板来自 DeviceProfile；只读 after locked。

## 6. 生命周期
Created → Locked（ScanTask 完成）→ Archived。

## 7. 状态
mutable until ScanTask enters Completed/Failed。

## 8. 文件系统映射
`{project}/devices/snapshots/{snapshotId}.json`

## 9. UI
报告/扫描详情只读展示。

## 10. Qt
ScanTask.start() 时 deep copy 当前设备配置。

## 11. 禁止
禁止用户编辑 locked snapshot；禁止 Profile 变更 retroactive 修改。

## 相关
[../../data/Device_Snapshot.md](../../data/Device_Snapshot.md)
