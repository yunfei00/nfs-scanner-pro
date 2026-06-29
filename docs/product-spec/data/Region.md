# Region

## 定义

Region 表示 PCB 上的一个扫描区域。

Region 是 Project 内最重要的工作单元。

一个 Project 可以包含多个 Region，例如 CPU、WiFi、PMIC、GNSS。

## 职责

Region 负责组织某一个扫描区域相关的所有信息：

- 区域名称
- 区域描述
- 起点和终点
- Z 高度
- 对齐数据 Alignment
- 扫描配置
- Hx 扫描
- Hy 扫描
- 分析结果
- 导出结果

## 命名规则

Region 必须有名称。

推荐名称：

- CPU
- WiFi
- PMIC
- GNSS
- USB
- Memory

不推荐只使用 Area001、Area002 这类无业务含义的名称。

## 起点和终点

Region 的真实设置流程是：

1. 用户手动移动探头到起点。
2. 软件记录起点。
3. 用户手动移动探头到终点。
4. 软件记录终点。
5. 软件生成区域范围和路径预览。

## Alignment

Alignment 属于 Region。

Project 可以保存整块 PCB 图片，但图像上的矩形、坐标映射、旋转、翻转、透明度等属于每个 Region。

## 生命周期

- Created：Region 已创建并命名。
- Positioned：起点和终点已保存。
- Aligned：图像对齐已完成，可选。
- Configured：扫描参数已设置。
- Scanned：至少完成一次扫描。
- Analyzed：已有分析结果。
- Reported：已进入报告。

## 规则

- 没有 Project，不能创建 Region。
- 没有 Region，不能开始 Scan。
- Region 可以没有 Alignment，但不能没有起点和终点。
- Region 删除前必须提醒用户关联的 Scan 和 Analysis 会受影响。
