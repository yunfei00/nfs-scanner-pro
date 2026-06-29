# Qt State Property Rules — 状态属性规则

## 设计目标

QSS 通过动态属性表达 variant/error/role，避免多份 parallel stylesheet。

## 标准属性

| 属性 | 值 | 用于 |
|---|---|---|
| variant | primary, secondary, danger | QPushButton |
| danger | true | QToolButton 停止 |
| error | true | QLineEdit 校验 |
| role | formLabel, formUnit | QLabel |
| accordionHeader | true | Accordion QToolButton |

## 设置后刷新样式

```text
widget.setProperty("variant", "primary")
widget.style().unpolish(widget)
widget.style().polish(widget)
```

## 与 State Token

`state.control.*` → QSS 伪状态；设备/扫描状态 → 代码改 icon/color，非 QSS property。

## 禁止事项

- 禁止用 objectName 后缀 `_error` 切换态（用 property）
- 禁止 property 名与 Qt 内置冲突

## 相关

- `../01_Foundation/State_Tokens.md`
- `../06_QSS/token_mapping_qss.md`
