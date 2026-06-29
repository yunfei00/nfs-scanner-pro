# Spacing Tokens — 间距与布局令牌

> 完整索引见 [Design_Tokens.md](Design_Tokens.md) §4

## 设计目标

8px 栅格 + Release 008 固定区域高度，保证画布 ≥70% 宽。

## 使用场景

主窗口布局、Dock 内边距、工具栏按钮间距、对话框 margin。

## 尺寸规则

```text
spacing.1~6 = 4 / 8 / 12 / 16 / 24 / 32 px
size.menubar.height     = 32px
size.toolbar.height     = 56px
size.deviceStatus.height = 40px
size.statusbar.height   = 32px
size.nav.collapsed      = 56px
size.nav.expanded       = 180px
size.dock.param.width   = 340px
size.canvas.minWidthPercent = 70
```

## Qt/PySide6 推荐组件

`QLayout.setContentsMargins(spacing.4, ...)`；`QMainWindow` dock 区域；Central `QHBoxLayout` stretch 给画布。

## objectName 命名建议

`centralWidget`、`graphicsWorkspace`、`leftNavigationBar`。

## 禁止事项

- 禁止导航默认 180px 常开
- 禁止画布宽 < 50%
- 禁止底部辅助 Dock 默认全显示

## 历史内容

吸收自 `../03_Spacing_And_Layout.md`。

## 相关文档

- [../03_Patterns/MainWindow_Pattern.md](../03_Patterns/MainWindow_Pattern.md)
