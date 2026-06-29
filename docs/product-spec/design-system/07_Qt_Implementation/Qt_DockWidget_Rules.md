# Qt DockWidget Rules — Dock 实现规则

## 设计目标

符合 Release 008 默认 layout 与 View Menu 联动。

## 初始化

```text
scanParamDock     → RightDockWidgetArea, visible=True
logDock           → BottomDockWidgetArea, visible=False
spectrumDock      → BottomDockWidgetArea, visible=False
statisticsDock    → BottomDockWidgetArea, visible=False
dataTableDock     → BottomDockWidgetArea, visible=False
```

## Features

`DockWidgetClosable | DockWidgetMovable | DockWidgetFloatable`

## 视图菜单

每个辅助 Dock 对应 checkable QAction；`toggled` ↔ `setVisible`。

## 重置布局

保存 `QMainWindow.saveState()` 默认 bytes；重置菜单 restore。

## 禁止事项

- 禁止 `addDockWidget(TopDockWidgetArea, ...)`
- 禁止辅助 Dock 默认 show

## 相关

- `../02_Components/DockPanel.md`
- `../04_Interaction/Dock_Interaction.md`
