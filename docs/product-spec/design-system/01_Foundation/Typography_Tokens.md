# Typography Tokens — 字体令牌

> 完整索引见 [Design_Tokens.md](Design_Tokens.md) §3

## 设计目标

简体中文实验室场景可读；坐标/频率/点数用等宽字体对齐。

## 使用场景

菜单、工具栏、Dock、状态栏、画布浮窗、表格数值列。

## 尺寸/颜色/状态规则

| 用途 | Token | 值 |
|---|---|---|
| 菜单 | typography.size.menu | 14px |
| 工具栏 | typography.size.toolbar | 14px |
| 正文 | typography.size.body | 13px |
| 说明 | typography.size.caption | 12px |
| 面板标题 | typography.size.panel.title | 16px |
| 主文字色 | color.text.primary | #EAF2FF |
| 次级文字 | color.text.secondary | #A8B3C2 |

## Qt/PySide6 推荐组件

`QApplication.setFont()`；数值列 `QStyledItemDelegate` + mono family。

## objectName 命名建议

`breadcrumbBar`、`statusBarMessageLabel`、`coordOverlayLabel`。

## 禁止事项

- 禁止正文 < 12px
- 禁止工具栏全大写英文
- 禁止画布中央大段文字

## 历史内容

吸收自 `../02_Typography.md`、`../02_Typography_Spacing.md`。
