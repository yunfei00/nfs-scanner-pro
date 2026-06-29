# PropertyPanel — 属性/参数面板（Accordion）

## 设计目标

scanParamDock 内五组 Accordion，扫描相关参数分组折叠。

## 使用场景

扫描设置、区域设置、显示设置、仪表设置、高级设置。

## 尺寸/颜色/状态规则

Dock 宽 340；组标题 40px；内容 padding `spacing.4`。默认：前两组展开，后三组折叠。

```text
扫描设置 [开]  区域设置 [开]  显示/仪表/高级 [关]
```

## Qt/PySide6 推荐组件

`QToolBox` 或自定义 Accordion（`QToolButton` checkable + 内容区）；内嵌 `QFormLayout`。

## objectName 命名建议

```text
scanSettingsGroup
regionSettingsGroup
displaySettingsGroup
instrumentSettingsGroup
advancedSettingsGroup
```

## 禁止事项

- 禁止五组全展开长滚动
- 禁止项目树占满 PropertyPanel

## 相关文档

- [../03_Patterns/Parameter_Dock_Pattern.md](../03_Patterns/Parameter_Dock_Pattern.md)
- 历史：`../10_Form_System.md`
