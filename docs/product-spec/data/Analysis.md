# Analysis

## 定义

Analysis 表示基于 Scan 数据生成的分析结果。

Analysis 不修改原始扫描数据。

## 职责

Analysis 负责保存：

- 使用的 Scan 数据
- 使用的 Region
- 选择的探头通道
- 选择的频点
- 选择的 Trace
- 显示模式
- 色带设置
- 数值范围
- 热力图结果
- 对比结果
- 用户结论

## 类型

第一版支持：

- Hx Heatmap
- Hy Heatmap
- Total Heatmap
- Frequency View
- Trace View
- Region Compare

## 与 Alignment 的关系

如果 Region 有有效 Alignment，Analysis 可以生成样品图片叠加图。

如果没有 Alignment，Analysis 仍然可以生成普通热力图。

## 规则

- Analysis 属于 Region。
- Analysis 引用 Scan 数据。
- Analysis 可以重复生成。
- Analysis 结果可以进入 Report。
- Analysis 不控制设备。

## 生命周期

- Created
- Configured
- Generated
- Reviewed
- Exported
