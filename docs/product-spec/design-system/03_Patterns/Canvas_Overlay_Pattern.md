# Canvas Overlay Pattern — 画布叠加模式

## 设计目标

小地图、色带、坐标浮窗在 Overlay 层，不抢 PCB 中心。

## 使用场景

扫描页、分析页热力图对比。

## 规则

- 热力图：单 QPixmapItem，opacity 0.7
- 色带：画布右缘，视图菜单 toggle
- 小地图：右下，视图菜单 toggle
- 坐标浮窗：跟随光标，z.canvas.overlay

## 禁止事项

- **禁止逐格 QGraphicsRectItem 热力图**
- 禁止 Overlay 挡 Breadcrumb

## 相关

- 历史：`../13_Heatmap_System.md`
- `../07_Qt_Implementation/Qt_GraphicsView_Rules.md`
