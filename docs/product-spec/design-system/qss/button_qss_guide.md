# 按钮 QSS 编写指南

> **历史兼容**：已迁移到 `06_QSS/form_qss.md`、`06_QSS/navigation_qss.md`、`06_QSS/toolbar_qss.md`。

> 主按钮、次按钮、危险按钮、工具栏按钮、导航按钮

## 设计目标

按钮层级清晰：扫描「开始」为主蓝，「停止/急停」为危险色，工具栏与导航为 flat 风格。

## 按钮类型

| 类型 | 用途 | 高度 | 圆角 |
|---|---|---:|---:|
| primary | 确定、开始扫描 | 36 | 6 |
| secondary | 取消、次要 | 36 | 6 |
| danger | 停止扫描、急停 | 36 | 6 |
| flat | 工具栏、导航 | 36 | 4 |
| icon-only | 工具栏 20px 图标 | 36 | 4 |

## QSS 结构建议

### 主按钮

```css
QPushButton[variant="primary"] {
    background-color: #0D6EFD;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    min-height: 36px;
    padding: 0 16px;
    font-weight: 500;
}

QPushButton[variant="primary"]:hover {
    background-color: #0B5ED7;
}

QPushButton[variant="primary"]:pressed {
    background-color: #0A58CA;
}

QPushButton[variant="primary"]:disabled {
    background-color: #0D6EFD40;
    color: #A8B3C2;
}
```

### 次按钮

```css
QPushButton[variant="secondary"] {
    background-color: transparent;
    color: #EAF2FF;
    border: 1px solid #1E2D3D;
    border-radius: 6px;
    min-height: 36px;
    padding: 0 16px;
}

QPushButton[variant="secondary"]:hover {
    background-color: #1E2D3D80;
}
```

### 危险按钮

```css
QPushButton[variant="danger"],
QPushButton[danger="true"] {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    min-height: 36px;
}

QPushButton[variant="danger"]:hover {
    background-color: #DC2626;
}

QPushButton[variant="danger"]:disabled {
    background-color: #6B7280;
    color: #A8B3C2;
}
```

### 工具栏停止按钮（objectName）

```css
QToolButton#toolbarStopScanButton {
    color: #EF4444;
}

QToolButton#toolbarStopScanButton:disabled {
    color: #6B7280;
}
```

### 导航按钮

```css
QWidget#leftNavigationBar QToolButton {
    background: transparent;
    border: none;
    border-radius: 4px;
    min-height: 48px;
    color: #A8B3C2;
}

QWidget#leftNavigationBar QToolButton:hover {
    background-color: #1E2D3D80;
    color: #EAF2FF;
}

QWidget#leftNavigationBar QToolButton:checked {
    background-color: #0D6EFD26;
    color: #0D6EFD;
    border-left: 3px solid #0D6EFD;
}
```

## 属性约定（Release 010）

- `setProperty("variant", "primary")` 后需 `style.unpolish/polish` 或统一 QSS 选择器
- 危险：`danger="true"` 或 `variant="danger"`

## objectName 示例

```text
toolbarStartScanButton
toolbarStopScanButton
dialogButtonOk
dialogButtonCancel
navScanButton
```

## 禁止事项

- 禁止所有按钮都用主蓝（失去层级）。
- 禁止停止扫描用绿色。
- 禁止按钮高度 < 32px 导致工业手套场景难点（V1 仍按 36px）。
- 禁止导航按钮使用 heavy border 3D 效果（非现代仪器风）。

## 相关文档

- `06_Toolbar_System.md`
- `07_Navigation_System.md`
- `10_Form_System.md`
- `dark_theme_tokens.qss.md`
