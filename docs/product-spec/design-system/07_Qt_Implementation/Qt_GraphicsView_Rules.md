# Qt GraphicsView Rules — 画布实现规则

## 设计目标

七层 Scene，热力图单 QPixmapItem。

## Scene 图层

| 层 | z Token | Item 类型 |
|---|---|---|
| PCB Photo | z.canvas.photo | QGraphicsPixmapItem |
| Heatmap | z.canvas.heatmap | QGraphicsPixmapItem |
| Grid | z.canvas.grid | QGraphicsItemGroup |
| Region | z.canvas.region | QGraphicsRectItem |
| Path | z.canvas.path | QGraphicsPathItem |
| Marker | z.canvas.marker | QGraphicsEllipseItem 等 |
| Overlay | z.canvas.overlay | QGraphicsProxyWidget |

## View 设置

- `setDragMode` 按 Canvas_Interaction 切换
- `setTransformationAnchor(AnchorUnderMouse)`
- 背景刷：`color.bg.canvas`

## 热力图（强制）

数据 → QImage → QPixmap → **一个** QGraphicsPixmapItem；`setOpacity(0.7)`。

## 禁止事项

- **禁止** for-loop QGraphicsRectItem 热力图格子
- 禁止 QOpenGLWidget 与 View 混用未评估（V1 默认 raster）

## 相关

- `../03_Patterns/Canvas_Overlay_Pattern.md`
- 历史：`../13_Heatmap_System.md`
