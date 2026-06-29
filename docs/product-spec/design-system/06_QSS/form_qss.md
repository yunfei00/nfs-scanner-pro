# Form & Button QSS — 表单与按钮

## 设计目标

Input/ComboBox/CheckBox/PushButton 统一 32/36px 高。

## QSS 片段

### 按钮（吸收 `../qss/button_qss_guide.md`）

```css
QPushButton[variant="primary"] {
    background-color: #0D6EFD;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    min-height: 36px;
    padding: 0 16px;
}

QPushButton[variant="secondary"] {
    background-color: transparent;
    color: #EAF2FF;
    border: 1px solid #1E2D3D;
    border-radius: 6px;
    min-height: 36px;
}

QPushButton[variant="danger"] {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    min-height: 36px;
}
```

### 输入（吸收 `../qss/form_qss_guide.md`）

```css
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #0B1724;
    color: #EAF2FF;
    border: 1px solid #1E2D3D;
    border-radius: 4px;
    min-height: 32px;
    padding: 4px 8px;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #0D6EFD;
}

QLineEdit[error="true"] {
    border: 1px solid #EF4444;
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
```

## 禁止事项

- 禁止 SpinBox 原生箭头未 style

## 相关

- [../02_Components/Input.md](../02_Components/Input.md)
