# Input — 输入框组件

## 设计目标

Dock 与对话框内紧凑可读，聚焦态明确。

## 使用场景

扫描步进、Z 高度、Region 名、设备 IP/端口、项目表单。

## 尺寸/颜色/状态规则

高 `size.input.height` = 32px；圆角 `radius.input`；背景 `color.bg.input`；边框 `color.border.default`；聚焦 `color.border.focus`；错误 `[error=true]` → `color.status.error` 边框。

## Qt/PySide6 推荐组件

`QLineEdit`、`QSpinBox`、`QDoubleSpinBox`；`QValidator`；标签 `QLabel[role=formLabel]`。

## objectName 命名建议

```text
fieldStepX
fieldStepY
fieldZHeight
fieldRegionName
fieldProjectName
```

## 禁止事项

- 禁止白色背景
- 禁止无 focus 样式
- 禁止扫描中修改步进无禁用态

## 相关文档

- [PropertyPanel.md](PropertyPanel.md)
- 历史：`../10_Form_System.md`
