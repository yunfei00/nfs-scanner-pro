# Alignment — 区域对齐

## 1. 对象定义
Region 与 PCB 图像、运动坐标之间的映射关系，**属于 Region**（ADR-0005）。

## 2. 为什么需要
叠加热力图、图像上标 Region、复现分析结果；**非扫描必要条件**。

## 3. 关键字段
imageRef, rectOnImage, motionBounds, transformMatrix, rotation, flipY, opacity, status。

## 4. 所属关系
0..1 属于 Region。

## 5. 与其它对象关系
引用 PCB 照片；被 Heatmap/Analysis 用于叠加。

## 6. 生命周期
Empty → Draft → Valid → Updated | Disabled。

## 7. 状态
见 [Alignment_State_Machine.md](../04_State_Machines/Alignment_State_Machine.md)。

## 8. 文件系统映射
`{region}/alignment.json`

## 9. UI 映射
工具栏「区域对齐」、画布 regionLayer。

## 10. Qt/PySide6 实现建议
保存 3×3 仿射矩阵；Scene 应用相同 transform 到 heatmap item。

## 11. 禁止事项
禁止存 Project 级唯一 Alignment 替代各 Region。

## 相关
[../../data/Alignment.md](../../data/Alignment.md)
