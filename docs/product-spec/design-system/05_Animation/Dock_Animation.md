# Dock Animation — Dock 动效

## 设计目标

auto-hide 收起/展开可预期，不闪屏。

## 规则

- auto-hide 离开边缘：`motion.slow` (300ms) 宽 → 40px
- 鼠标靠右边缘触发：200ms 展开 → 340px
- 显隐 toggle（视图菜单）：无动画或 150ms opacity（二选一，Release 010 统一）

## Qt

自定义 `QDockWidget` 或 resizeEvent + animation。

## objectName

`scanParamDock`。

## 禁止事项

- 禁止 bottom Dock slide 遮挡 statusBar
- 禁止动画期间丢失 mouse release

## 相关

- [Dock_Interaction.md](../04_Interaction/Dock_Interaction.md)
