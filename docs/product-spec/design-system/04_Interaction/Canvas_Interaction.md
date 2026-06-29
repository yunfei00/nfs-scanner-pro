# Canvas Interaction — 画布交互

## 设计目标

Altium 式 PCB 视图：平移、缩放、网格、测量。

## 使用场景

scanPage、analysisPage 热力图查看。

## 规则

- 默认 fit PCB，margin 5%
- 缩放 10%~800%，锚点 UnderMouse
- Space+左键 或 中键：平移
- 工具栏「网格」「测量」toggle Overlay 层
- 坐标浮窗跟随光标，显示 x/y/z

## Qt

`QGraphicsView`：`AnchorUnderMouse`、`ScrollHandDrag`（模式切换）。

## objectName

`scanCanvasView`、`scanScene`。

## 禁止事项

- 禁止 QLabel 代替 View 缩放
- 禁止缩放丢失 Alignment 变换

## 相关

- [../07_Qt_Implementation/Qt_GraphicsView_Rules.md](../07_Qt_Implementation/Qt_GraphicsView_Rules.md)
