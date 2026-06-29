# Tooltip — 工具提示组件

## 设计目标

图标按钮与画布工具简短说明，不遮挡 PCB 中心。

## 使用场景

工具栏 icon-only、导航图标、画布测量点。

## 尺寸/颜色/状态规则

背景 `color.bg.panel`；边框 `color.border.default`；文字 12px caption；圆角 `radius.tooltip`；阴影 `shadow.tooltip`；延迟 400ms；z `z.tooltip`。

## Qt/PySide6 推荐组件

`QToolTip` 全局样式 via QSS；`setToolTip()` on buttons。

## objectName 命名建议

无独立 objectName；宿主按钮保留原名。

## 禁止事项

- 禁止 Tooltip 显示长参数列表
- 禁止 Tooltip 挡画布中心常驻

## 相关文档

- [Design_Tokens.md](../01_Foundation/Design_Tokens.md) §9 z.tooltip
