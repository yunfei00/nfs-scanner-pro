# 01 PySide6 / Qt 布局实现规范

## 主窗口

```text
QMainWindow
├── QMenuBar
├── QToolBar
├── CentralWidget
│   ├── LeftNavigationBar
│   ├── DeviceStatusBar
│   ├── GraphicsWorkspace
│   └── RightDockArea
├── QDockWidget
└── QStatusBar
```

## 推荐类

```text
MainWindow
ScanPage
DevicePage
AnalysisPage
ReportPage
LeftNavigationBar
DeviceStatusBar
ScanCanvasView
ScanParameterDock
LogDock
SpectrumDock
StatisticsDock
```

## 主画布

QGraphicsView + QGraphicsScene。

图层：PCB Photo Layer、Heatmap Layer、Grid Layer、Region Layer、Path Layer、Marker Layer、Overlay UI Layer。

热力图必须整张 QPixmap 绘制，不允许逐格绘制。
