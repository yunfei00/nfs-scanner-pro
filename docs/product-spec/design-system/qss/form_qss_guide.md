# 表单控件 QSS 编写指南

> **历史兼容**：已迁移到 `06_QSS/form_qss.md`。

> QLineEdit、QComboBox、QSpinBox、QCheckBox、QGroupBox、QProgressBar

## 设计目标

表单控件在深色面板内可读、聚焦态明确，与 Keysight 仪器设置面板类似，非 Material Design 浮动标签。

## 适用场景

- scanParamDock 内 Accordion 表单
- 对话框表单
- 设备页连接参数

## QSS 结构建议

### QLineEdit / QSpinBox / QDoubleSpinBox

```css
QLineEdit,
QSpinBox,
QDoubleSpinBox {
    background-color: #0B1724;
    color: #EAF2FF;
    border: 1px solid #1E2D3D;
    border-radius: 4px;
    min-height: 32px;
    padding: 4px 8px;
    selection-background-color: #0D6EFD;
}

QLineEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border: 1px solid #0D6EFD;
}

QLineEdit:disabled,
QSpinBox:disabled,
QDoubleSpinBox:disabled {
    color: #6B7280;
    background-color: #07111D;
}

QLineEdit[error="true"] {
    border: 1px solid #EF4444;
}
```

### QComboBox

```css
QComboBox {
    background-color: #0B1724;
    color: #EAF2FF;
    border: 1px solid #1E2D3D;
    border-radius: 4px;
    min-height: 32px;
    padding: 4px 8px;
}

QComboBox:focus {
    border: 1px solid #0D6EFD;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #0B1724;
    color: #EAF2FF;
    border: 1px solid #1E2D3D;
    selection-background-color: #0D6EFD33;
}
```

### QCheckBox / QRadioButton

```css
QCheckBox {
    color: #EAF2FF;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #1E2D3D;
    border-radius: 3px;
    background-color: #0B1724;
}

QCheckBox::indicator:checked {
    background-color: #0D6EFD;
    border-color: #0D6EFD;
}

QCheckBox:disabled {
    color: #6B7280;
}
```

### QLabel 表单标签

```css
QLabel[role="formLabel"] {
    color: #A8B3C2;
    font-size: 13px;
}

QLabel[role="formUnit"] {
    color: #A8B3C2;
    font-size: 12px;
}
```

### QProgressBar（状态栏 / 扫描）

```css
QProgressBar {
    background-color: #07111D;
    border: 1px solid #1E2D3D;
    border-radius: 4px;
    text-align: center;
    color: #EAF2FF;
    min-height: 16px;
    max-height: 16px;
}

QProgressBar::chunk {
    background-color: #3B82F6;
    border-radius: 3px;
}
```

### QGroupBox（对话框可选）

```css
QGroupBox {
    color: #EAF2FF;
    border: 1px solid #1E2D3D;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #A8B3C2;
}
```

## 属性约定

- `error="true"` on QLineEdit 显示校验失败
- `role="formLabel"` on QLabel 区分标签与数值

## 禁止事项

- 禁止输入框白色背景 `#FFFFFF`。
- 禁止去掉 focus 边框（键盘导航不可见）。
- 禁止 SpinBox 按钮使用 OS 原生箭头不 styling。
- 禁止表单控件 font-size < 12px。

## 相关文档

- `10_Form_System.md`
- `11_Table_System.md`（表格另见排版规范）
- `dark_theme_tokens.qss.md`
