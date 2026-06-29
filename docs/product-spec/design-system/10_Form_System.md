# 10 表单系统规范

> **历史兼容**：该文档已迁移到 `02_Components/Input.md`、`ComboBox.md`、`PropertyPanel.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Form System

## 设计目标

右侧参数 Dock 内表单紧凑、分组清晰，支持工程师快速修改扫描参数；Accordion 折叠低频项，避免滚动距离过长。

## 使用场景

- 扫描参数 Dock 五组 Accordion
- 对话框内项目信息、Region 命名
- 设备页连接参数（端口、波特率、IP）
- 设置页系统选项

## Accordion 分组（扫描参数 Dock）

| 组 | 默认 | 典型字段 |
|---|---|---|
| 扫描设置 | 展开 | X/Y 步进、Z 高度、速度、驻留时间 |
| 区域设置 | 展开 | Region 名、起点/终点、通道 Hx/Hy |
| 显示设置 | 折叠 | 网格、热力图透明度、色带 |
| 仪表设置 | 折叠 | 频率、迹线、RBW/VBW |
| 高级设置 | 折叠 | 蛇形模式、补偿、调试选项 |

## 控件尺寸

| 控件 | 高度 | 圆角 | 背景 | 边框 |
|---|---:|---:|---|---|
| QLineEdit | 32 | 4 | `--color-input-bg` | `--color-border` |
| QComboBox | 32 | 4 | 同上 | 同上 |
| QSpinBox / QDoubleSpinBox | 32 | 4 | 同上 | 同上 |
| QCheckBox | 24 行高 | — | 透明 | — |
| 主按钮 | 36 | 6 | `--color-primary` | none |
| 次按钮 | 36 | 6 | transparent | `--color-border` |
| 危险按钮 | 36 | 6 | `--color-status-error` | none |

聚焦：边框 `--color-input-focus`，1px 外发光可选（QSS box-shadow 模拟）。

## 标签规则

- 标签在控件上方（Dock 窄宽）或左侧（对话框宽表单）。
- 标签 13px `--color-text-secondary`。
- 必填项标签后加 `*`（error 色）。
- 单位与数值同行右对齐：`120.0 mm`。

## 状态规则

| 状态 | 表现 |
|---|---|
| 正常 | 默认可编辑 |
| 只读 | 灰底，`read-only` QSS |
| 禁用 | `--color-status-idle` 文字 |
| 校验错误 | 红框 + 下方 12px 错误文案 |
| 扫描中 | 影响安全的字段禁用（步进、区域范围） |

## Qt/PySide6 推荐组件

- `QFormLayout` 或 `QGridLayout`（两列：标签 + 控件）
- 分组：`QGroupBox` 或自定义 Accordion（`QToolButton` checkable + 内容 `QWidget`）
- 数值：`QDoubleSpinBox` 保留足够 decimals
- 长列表：`QComboBox` editable=false
- 校验：`QValidator` + 错误 label

## objectName 命名建议

```text
scanSettingsGroup
regionSettingsGroup
displaySettingsGroup
instrumentSettingsGroup
advancedSettingsGroup
fieldStepX
fieldStepY
fieldZHeight
fieldScanSpeed
fieldDwellTime
fieldRegionName
fieldProbeChannel
fieldCenterFrequency
fieldTraceSelection
```

## 禁止事项

- 禁止在表单内使用 card 套 card 超过 2 层嵌套。
- 禁止 Accordion 全部默认展开导致 Dock 需长滚动。
- 禁止用原生 OS 浅色表单风格（必须 QSS 深色）。
- 禁止扫描关键参数无单位标注。
- 禁止在画布上直接放置大量表单控件。

## 相关文档

- Dock：`08_Dock_System.md`
- 旧版：`03_Component_Rules.md`
- QSS：`qss/form_qss_guide.md`
