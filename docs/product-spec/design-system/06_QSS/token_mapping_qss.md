# Token Mapping QSS — 设计令牌与 QSS 映射

## 设计目标

`Design_Tokens.md` 点分命名与 QSS 属性值一一对应，支持构建时替换。

## 映射表（节选）

| Design Token | 旧别名 (--*) | QSS 属性示例 |
|---|---|---|
| color.bg.app | --color-bg-deep | background-color |
| color.bg.panel | --color-bg-panel | background-color |
| color.text.primary | --color-text-primary | color |
| color.brand.primary | --color-primary | background-color |
| color.border.default | --color-border | border |
| color.status.success | --color-status-ok | color / background |
| spacing.4 | --space-4 | padding, margin |
| radius.button | --radius-button | border-radius |
| size.toolbar.height | --height-toolbar | min-height, max-height |
| motion.normal | — | QPropertyAnimation duration |

## 替换语法（Release 010）

```text
@color.bg.app@  →  #07111D
@size.toolbar.height@  →  56px
```

Python 示例（文档化）：

```text
qss = template.replace("@color.bg.app@", TOKENS["color.bg.app"])
```

## 伪状态映射

| state.control.* | QSS |
|---|---|
| hover | :hover |
| pressed | :pressed |
| focus | :focus |
| disabled | :disabled |
| checked | :checked |
| error | [error="true"] |

## 动态属性

| 属性 | 组件 | QSS |
|---|---|---|
| variant=primary | QPushButton | 见 form_qss |
| variant=danger | QPushButton | 见 form_qss |
| danger=true | QToolButton | #toolbarStopScanButton |
| accordionHeader=true | QToolButton | 见 dock_qss |
| role=formLabel | QLabel | color secondary |

## Qt/PySide6

`QApplication.setStyleSheet()` 一次加载；`setProperty` 后 `polish/unpolish`。

## 禁止事项

- 禁止 QSS 内未映射的新 hex
- 禁止 Token 与映射表不一致不更新

## 相关

- [../01_Foundation/Design_Tokens.md](../01_Foundation/Design_Tokens.md)
- 历史：`../qss/dark_theme_tokens.qss.md`
