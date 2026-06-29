# MainWindow Pattern — 主窗口模式

## 设计目标

1920×1080 固定分层 shell，PCB 画布 stretch 最大。

## 使用场景

应用唯一主窗口 `QMainWindow`。

## 结构

```text
QMenuBar (32)
QToolBar (56)
CentralWidget
  DeviceStatusBar (40)
  HBox: Nav(56↔180) | Canvas(stretch) | [Dock area]
QDockWidgets (bottom, hidden default)
QStatusBar (32)
```

## Qt 组件

见 `07_Qt_Implementation/Qt_Widget_Mapping.md`。

## objectName

`mainWindow`、`centralWidget`、`pageStack`。

## 禁止事项

- 禁止多 Document MDI 为主模式
- 禁止 Central 无 canvas stretch

## 相关

- `../../ui-wireframe/01_Main_Window_1920x1080.md`
- `../01_Foundation/Spacing_Tokens.md`
