# 12 主画布 QGraphicsView 规范

> **历史兼容**：该文档已迁移到 `07_Qt_Implementation/Qt_GraphicsView_Rules.md` 与 `03_Patterns/Canvas_Overlay_Pattern.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · GraphicsView System

## 设计目标

PCB 照片与热力图为视觉主角，主画布占据最大面积；通过 QGraphicsView 分层渲染实现缩放、平移、Region 编辑与路径预览，交互参考 Altium / Cadence PCB 视图。

## 使用场景

- 显示 PCB 样品照片
- 叠加热力图、Region 矩形、扫描网格、路径
- 网格、测量、小地图、坐标浮窗
- Breadcrumb 上下文条（画布顶部 overlay，非菜单）

## 图层顺序（从底到顶）

| 顺序 | 图层 | Z 值建议 | 内容 |
|---|---|---:|---|
| 1 | PCB Photo Layer | 0 | 样品照片 QGraphicsPixmapItem |
| 2 | Heatmap Layer | 10 | 热力图 QGraphicsPixmapItem，可调透明度 |
| 3 | Grid Layer | 20 | 网格线 |
| 4 | Region Layer | 30 | Region 矩形、选中框 |
| 5 | Path Layer | 40 | 扫描路径、蛇形点序 |
| 6 | Marker Layer | 50 | 起点/终点、当前探头位置 |
| 7 | Overlay UI Layer | 100 | 小地图、色带、坐标浮窗（Widget 或 Item） |

## 尺寸与行为

| 属性 | 规则 |
|---|---|
| 最小宽度占比 | ≥ 70% 窗口内容区 |
| 背景色 | `--color-canvas-bg` |
| 默认缩放 | fit 整板可见，保留 5% margin |
| 缩放范围 | 10% ~ 800% |
| 平移 | 中键拖拽或 Space+左键 |
| 滚轮 | 以光标为中心缩放 |

## Breadcrumb（画布内顶部）

```text
项目 > CPU_Area > Hx Probe > 2.450 GHz > 6461 pts
```

高度 28px，半透明底 `--color-bg-panel` 80% opacity，不遮挡 PCB 中心。

## Qt/PySide6 推荐组件

- `QGraphicsView` + `QGraphicsScene`
- 抗锯齿：照片 off，热力图 off，标记/路径可选 on
- 变换：`setTransformationAnchor(QGraphicsView.AnchorUnderMouse)`
- 图层：独立 `QGraphicsItemGroup` 或 zValue
- Overlay：`QGraphicsProxyWidget` 嵌入小地图
- 性能：`QGraphicsView.setViewportUpdateMode(BoundingRectViewportUpdate)` 扫描时

## objectName 命名建议

```text
scanCanvasView
scanScene
pcbPhotoLayer
heatmapLayer
gridLayer
regionLayer
pathLayer
markerLayer
overlayLayer
breadcrumbBar
minimapWidget
colorBarWidget
coordOverlayLabel
```

## 禁止事项

- 禁止用 QLabel 单图替代 QGraphicsView 做缩放平移。
- 禁止在 CentralWidget 用 QSplitter 把画布压到小于 50% 宽。
- 禁止热力图用 thousands of QGraphicsRectItem 逐格绘制（见 `13_Heatmap_System.md`）。
- 禁止 Breadcrumb 放入菜单栏或工具栏。
- 禁止画布 background 使用高对比棋盘格抢视觉（浅网格即可）。

## 相关文档

- 线框：`ui-wireframe/05_Scan_Page_Wireframe.md`
- 热力图：`13_Heatmap_System.md`
- Qt：`qt-spec/01_Qt_Layout_Spec.md`
