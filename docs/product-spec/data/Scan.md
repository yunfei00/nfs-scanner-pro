# Scan

## 定义

Scan 表示 Region 下的一次真实采集任务。

Scan 不是 Project，也不是 Region。

Scan 是带有时间、设备快照、扫描参数、探头通道和原始数据的一次采集记录。

## 职责

Scan 负责保存：

- 所属 Project
- 所属 Region
- 探头通道 Hx 或 Hy
- 扫描参数
- 设备快照
- 开始时间和结束时间
- 扫描状态
- 原始数据
- 处理数据
- 错误信息

## 探头通道

支持：

- Hx
- Hy

第一版商业软件推荐：

先完整扫描 Hx，再完整扫描 Hy。

不推荐每个点都切换 Hx 和 Hy。

## 状态

- Pending：等待扫描。
- Running：正在扫描。
- Paused：暂停。
- Completed：完成。
- Failed：失败。
- Cancelled：取消。

## 规则

- Scan 必须属于一个 Region。
- Scan 启动前必须检查 Motion 和 Spectrum。
- Camera 不在线不能阻止 Scan。
- 每次 Scan 的原始数据不能被覆盖。
- 重新扫描应创建新的 Scan 记录。

## 生命周期

- Created
- Queued
- Running
- Finished
- Verified
- Archived

## 关联对象

- Region：一对多。
- Device Snapshot：每次 Scan 可以保存一个快照。
- Analysis：一个 Scan 可以产生多个分析结果。
