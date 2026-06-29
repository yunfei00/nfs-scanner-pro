# Button — 按钮组件

## 设计目标

清晰操作层级：主蓝开始、红危险停止、flat 工具/导航。

## 使用场景

工具栏扫描控制、对话框确认、Dock 内次要动作、导航项。

## 尺寸/颜色/状态规则

| 变体 | 高 | 圆角 | 背景 Token |
|---|---:|---:|---|
| primary | 36 | radius.button | color.brand.primary |
| secondary | 36 | radius.button | transparent + border |
| danger | 36 | radius.button | color.status.error |
| flat/icon | 36 | radius.nav.item | transparent |

状态：hover → primary.hover；disabled → primary.disabled / text.disabled。

## Qt/PySide6 推荐组件

`QPushButton`（对话框）、`QToolButton`（工具栏/导航）；`setProperty("variant","primary")`。

## objectName 命名建议

```text
toolbarStartScanButton
toolbarStopScanButton
dialogButtonOk
dialogButtonCancel
navScanButton
```

## 禁止事项

- 禁止全部主蓝
- 禁止停止扫描绿色
- 禁止高度 < 32px

## 相关文档

- [../06_QSS/form_qss.md](../06_QSS/form_qss.md)（含 button 片段）
- 历史：`../06_Toolbar_System.md`
