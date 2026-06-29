# Dock QSS — Dock 面板

## 设计目标

32px 标题栏，scanParamDock 左蓝标识。

## objectName

`scanParamDock`、`logDock`、`spectrumDock`、`statisticsDock`、`dataTableDock`。

## QSS 片段

（吸收自 `../qss/dock_widget_qss_guide.md` 全文）

```css
QDockWidget {
    color: #EAF2FF;
}

QDockWidget::title {
    background-color: #0B1724;
    text-align: left;
    padding-left: 12px;
    padding-top: 6px;
    min-height: 32px;
    max-height: 32px;
    font-size: 14px;
    font-weight: 600;
    border-bottom: 1px solid #1E2D3D;
}

QDockWidget::close-button,
QDockWidget::float-button {
    background: transparent;
    border: none;
    padding: 4px;
}

QDockWidget::close-button:hover,
QDockWidget::float-button:hover {
    background-color: #1E2D3D80;
}

QDockWidget > QWidget {
    background-color: #0B1724;
    border: 1px solid #1E2D3D;
}

QDockWidget#scanParamDock::title {
    border-left: 3px solid #0D6EFD;
}

QToolButton[accordionHeader="true"] {
    background-color: #07111D;
    color: #EAF2FF;
    border: none;
    border-bottom: 1px solid #1E2D3D;
    padding: 10px 16px;
    text-align: left;
    font-weight: 600;
}

QToolButton[accordionHeader="true"]:checked {
    border-left: 3px solid #0D6EFD;
}
```

## 禁止事项

- 禁止 Dock 标题 > 36px
- 禁止内容区白底

## 相关

- [../02_Components/DockPanel.md](../02_Components/DockPanel.md)
