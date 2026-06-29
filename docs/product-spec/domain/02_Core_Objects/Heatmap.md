# Heatmap — 热力图

## 1. 对象定义
由 ScanTask 的 ScanPoint 场强数据生成的 **2D 栅格图像**（ADR-0010）。

## 2. 为什么需要
分析页、画布叠加、报告图；与 raw 分离可重算。

## 3. 关键字段
heatmapId, scanTaskId, probeChannel, lut, minValue, maxValue, imagePath, width, height, overlayOpacity。

## 4. 所属关系
属于 ScanTask；可多个（不同 LUT/插值）。

## 5. 与其它对象关系
引用 Alignment 做叠加；Analysis 引用 Heatmap。

## 6. 生命周期
见 [Heatmap_Lifecycle.md](../05_Lifecycle/Heatmap_Lifecycle.md)。

## 7. 状态
Generating → Ready → Stale（raw 变更后）。

## 8. 文件系统映射
`processed/heatmap_{id}.png` + `heatmap_{id}.json` 元数据

## 9. UI 映射
heatmapLayer **单 QPixmap**；色带 Overlay。

## 10. Qt/PySide6 实现建议
离线生成 PNG；Scene 只加载 pixmap，**禁止逐格 Item**。

## 11. 禁止事项
禁止热力图生成改写 raw；禁止逐格绘制（ADR-0010）。

## 相关
[../../decision/ADR-0010-Heatmap.md](../../decision/ADR-0010-Heatmap.md)
