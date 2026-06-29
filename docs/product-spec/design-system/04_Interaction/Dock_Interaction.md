# Dock Interaction — Dock 交互

## 设计目标

用户可固定、隐藏、关闭、拖放 Dock；辅助 Dock 默认不出现。

## 使用场景

参数/日志/频谱/统计/表格 Dock。

## 规则

- 关闭 × → hidden，视图菜单可 reopen
- 拖放：左/右/底合法；**顶栏非法**，拖至顶自动回弹
- auto-hide：仅 scanParamDock 可选，离开 300ms 收起至 40px
- 重置布局：恢复 008 默认 visibility 与 geometry

## Qt

`QDockWidget` features：`DockWidgetClosable | DockWidgetMovable | DockWidgetFloatable`。

## objectName

`scanParamDock`、`logDock` 等。

## 禁止事项

- 禁止辅助 Dock 启动 visible
- 禁止 float 后丢失 QSS

## 相关

- [Dock_Animation.md](../05_Animation/Dock_Animation.md)
- [View_Menu_Dock_Pattern.md](../03_Patterns/View_Menu_Dock_Pattern.md)
