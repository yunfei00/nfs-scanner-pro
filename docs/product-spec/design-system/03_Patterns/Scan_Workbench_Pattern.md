# Scan Workbench Pattern — 扫描工作台模式

## 设计目标

工程师 90% 时间所在：Nav + Canvas + Param Dock + Breadcrumb。

## 使用场景

默认首页 scanPage。

## 布局

```text
Left Nav | Breadcrumb + QGraphicsView (PCB/Heatmap/Region/Path) | scanParamDock
```

画布层 z 序见 Design_Tokens §9。

## 组件组合

NavigationBar + Breadcrumb + ScanCanvasView + PropertyPanel + ToolBar + StatusBar。

## 禁止事项

- 禁止扫描页变 Dashboard 卡片墙
- 禁止参数放 Dialog 为主编辑

## 相关

- `../../ui-wireframe/05_Scan_Page_Wireframe.md`
- 历史：`../12_GraphicsView_System.md`
