# 13 热力图系统规范

> **历史兼容**：该文档已迁移到 `03_Patterns/Canvas_Overlay_Pattern.md` 与 `07_Qt_Implementation/Qt_GraphicsView_Rules.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Heatmap System

## 设计目标

热力图以**整张位图**叠加在 PCB 图层之上，支持 Turbo LUT、透明度调节与 Hx/Hy 切换，渲染性能满足数千至数万扫描点，符合 ADR-0010。

## 使用场景

- 扫描完成后生成 2D 场强分布
- 扫描过程中增量刷新（可选，Mock 阶段可整图替换）
- 分析页对比 Hx / Hy / 合成结果
- 与样品照片对齐叠加

## 渲染规则（强制）

1. 数据 → 2D 数组 → 颜色映射（Turbo LUT）→ **单张 `QImage` / `QPixmap`**
2. 使用 `QGraphicsPixmapItem` 置于 Heatmap Layer
3. 透明度默认 **70%**（`--heatmap-overlay-opacity`），显示设置可调 0~100%
4. 坐标与 Region Alignment 一致，仿射变换与 PCB 照片共享
5. Hx、Hy、Total 各缓存独立 pixmap，切换不重算除非数据变

## 色带（Color Bar）

- 位置：画布右侧 Overlay，宽 24px，高 200px 起
- LUT：Turbo（默认），Settings 可扩展 Jet / Viridis（V2）
- 标注：min / max 数值，13px 等宽
- 经视图菜单「显示色带」切换

## 尺寸与性能

| 属性 | 规则 |
|---|---|
| 栅格分辨率 | 与扫描点阵一致，上采样双线性 |
| 最大边长 | 建议 ≤ 4096 px 纹理 |
| 刷新频率 | 扫描中 ≤ 2 fps 整图更新 |
| 内存 | 释放旧 QPixmap 再赋值 |

## 状态规则

| 状态 | 表现 |
|---|---|
| 无数据 | 不显示 Heatmap Layer |
| 扫描中 | 部分更新或进度色 |
| Hx 模式 | 显示 Hx pixmap |
| Hy 模式 | 显示 Hy pixmap |
| 合成 | Total pixmap，分析页默认 |

## Qt/PySide6 推荐组件

- 生成：`numpy` 数组 → `QImage.Format_ARGB32` → `QPixmap.fromImage`
- 显示：`QGraphicsPixmapItem`，`setOpacity(0.7)`
- LUT：预计算 256 色表，Release 010 实现于 `HeatmapService`
- **禁止**：循环 `QGraphicsRectItem` 或 `QPainter.drawRect`  per cell on Scene

## objectName 命名建议

```text
heatmapLayer
heatmapPixmapItem
colorBarWidget
fieldOpacitySlider
channelSelectorHx
channelSelectorHy
channelSelectorTotal
```

## 禁止事项

- **禁止逐格绘制**（ADR-0010、qt-spec 强制）。
- 禁止热力图修改原始扫描数据。
- 禁止在 QWidget 全屏 QLabel 刷新实现实时扫描（须 Scene 层 pixmap）。
- 禁止默认 100% 不透明遮挡 PCB 细节。
- 禁止未对齐时强行拉伸热力图到照片（须按 Alignment 变换）。

## 相关文档

- ADR：`decision/ADR-0010-Heatmap.md`
- 画布：`12_GraphicsView_System.md`
- 颜色：`01_Color_System.md`（Turbo LUT）
