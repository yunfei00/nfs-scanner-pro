# Radius & Shadow Tokens — 圆角与阴影

> 完整索引见 [Design_Tokens.md](Design_Tokens.md) §5–§6

## 设计目标

小圆角工业风，避免 Consumer App 大圆角；阴影克制。

## 使用场景

按钮、输入框、对话框、Tooltip、浮动 Dock。

## 尺寸/颜色/状态规则

```text
radius.input   = 4px
radius.button  = 6px
radius.panel   = 8px
radius.dialog  = 8px
shadow.panel   = 0 2px 8px rgba(0,0,0,0.35)
shadow.dialog  = 0 8px 24px rgba(0,0,0,0.55)
```

面板分隔优先 1px `color.border.default`，非阴影。

## Qt/PySide6 推荐组件

QSS `border-radius`；`QDialog` 内容区；浮动 Dock 用系统标题栏。

## objectName 命名建议

通用，见各 Component 文档。

## 禁止事项

- 禁止 16px+ 大圆角 card
- 禁止画布内元素 heavy drop-shadow

## 相关文档

- [Design_Tokens.md](Design_Tokens.md)
