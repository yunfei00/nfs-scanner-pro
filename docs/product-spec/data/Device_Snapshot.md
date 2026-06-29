# Device Snapshot

## 定义

Device Snapshot 是某个时刻设备配置和状态的记录。

它用于保证 Project 和 Scan 可以追溯。

## 职责

Device Snapshot 负责记录扫描发生时使用的设备配置。

包括：

- 运动控制器配置
- 频谱仪配置
- 相机配置，可选
- 探头舵机配置，可选
- 软件版本
- 配置来源
- 时间戳

## 与 Device Profile 的关系

Device Profile 是系统级模板。

Device Snapshot 是 Project 或 Scan 保存的副本。

修改 Device Profile 不影响已经保存的 Snapshot。

## 保存位置

Project 可以保存一次 Project-level Snapshot。

每次 Scan 也可以保存 Scan-level Snapshot。

Scan-level Snapshot 用于最严格的结果复现。

## 规则

- Snapshot 只记录，不控制设备。
- Snapshot 不应该被用户随意修改。
- Snapshot 用于报告、审计、复现和问题排查。

## 生命周期

- Created：生成快照。
- Locked：随 Scan 完成后锁定。
- Archived：随 Project 归档。
