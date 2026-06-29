# CheckBox — 复选框组件

## 设计目标

显示设置、蛇形模式等开关，16px 指示器。

## 使用场景

显示设置 Accordion、视图菜单 checkable 项联动、表单选项。

## 尺寸/颜色/状态规则

指示器 16×16；未选 border `color.border.default`；选中 fill `color.brand.primary`；disabled `color.text.disabled`。

## Qt/PySide6 推荐组件

`QCheckBox`、`QRadioButton`（Hx/Hy 互斥组）。

## objectName 命名建议

```text
fieldSnakeMode
fieldShowGrid
actionShowLogDock
```

## 禁止事项

- 禁止原生 OS unchecked 白底

## 相关文档

- [../06_QSS/form_qss.md](../06_QSS/form_qss.md)
