# ComboBox — 下拉框组件

## 设计目标

频点、迹线、Region 列表等枚举选择，与 Input 视觉一致。

## 使用场景

频率选择、迹线、探头通道 Hx/Hy、设备 Profile。

## 尺寸/颜色/状态规则

同 Input 32px 高；下拉列表背景 `color.bg.panel`；选中项 `color.table.selected`。

## Qt/PySide6 推荐组件

`QComboBox`；`QAbstractItemView` 样式见 QSS；editable 默认 false。

## objectName 命名建议

```text
fieldProbeChannel
fieldTraceSelection
fieldDeviceProfile
```

## 禁止事项

- 禁止 editable 除非明确需求
- 禁止下拉列表浅色原生样式

## 相关文档

- [../06_QSS/form_qss.md](../06_QSS/form_qss.md)
