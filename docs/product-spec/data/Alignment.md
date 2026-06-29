# Alignment

## 定义

Alignment 表示扫描区域与样品图像、运动坐标之间的对应关系。

Alignment 属于 Region。

## 职责

Alignment 负责保存：

- 引用的样品图片
- 图像上的区域框
- 实际运动坐标范围
- 坐标映射关系
- 上下翻转设置
- 旋转设置
- 透明度设置
- 标定状态

## 规则

- Alignment 不是扫描的必要条件。
- 没有 Alignment 时，仍然可以扫描。
- 没有 Alignment 时，仍然可以生成普通热力图。
- 有 Alignment 时，可以进行样品图片叠加显示。
- 每个 Region 有自己的 Alignment。

## 与 Sample 的关系

Sample 图片属于 Project。

Region 的 Alignment 引用 Sample 图片，并保存该 Region 在图片上的位置和映射信息。

## 生命周期

- Empty：未对齐。
- Draft：用户正在编辑。
- Valid：对齐已确认。
- Updated：对齐被重新调整。
- Disabled：该 Region 不使用对齐。

## 使用场景

- 在样品图片上画扫描区域。
- 将扫描数据映射到图片上。
- 生成叠加热力图。
- 重新打开项目后复现上次分析结果。
