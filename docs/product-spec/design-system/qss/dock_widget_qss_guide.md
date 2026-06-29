# Dock Widget QSS 编写指南

> **历史兼容**：已迁移到 `06_QSS/dock_qss.md`。

> QDockWidget 标题栏、内容区、浮动与 tab 化状态

## 设计目标

Dock 面板与主窗口深色主题融合，标题栏 32px 紧凑，右侧参数 Dock 与底部辅助 Dock 视觉一致。

## 适用 objectName

```text
scanParamDock
logDock
spectrumDock
statisticsDock
dataTableDock
```

## QSS 结构建议

### QDockWidget 基础

```css
QDockWidget {
    color: #EAF2FF;
    titlebar-close-icon: url(:/icons/dock-close.svg);
    titlebar-normal-icon: url(:/icons/dock-float.svg);
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
```

### 内容区

```css
QDockWidget > QWidget {
    background-color: #0B1724;
    border: 1px solid #1E2D3D;
}
```

### 按 Dock 区分（可选）

```css
QDockWidget#scanParamDock::title {
    border-left: 3px solid #0D6EFD;
}
```

### Tab 化底部 Dock

```css
QTabBar::tab {
    background-color: #07111D;
    color: #A8B3C2;
    padding: 8px 16px;
    border: 1px solid #1E2D3D;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #0B1724;
    color: #EAF2FF;
    border-bottom: 2px solid #0D6EFD;
}
```

## Accordion 标题（Dock 内部，自定义 widget）

```css
QToolButton[accordionHeader="true"] {
    background-color: #07111D;
    color: #EAF2FF;
    border: none;
    border-bottom: 1px solid #1E2D3D;
    padding: 10px 16px;
    text-align: left;
    font-weight: 600;
}

QToolButton[accordionHeader="true"]:hover {
    background-color: #1E2D3D80;
}

QToolButton[accordionHeader="true"]:checked {
    border-left: 3px solid #0D6EFD;
}
```

## 禁止事项

- 禁止 Dock 标题栏高度 > 36px。
- 禁止 Dock 内容区白色背景。
- 禁止关闭 Dock 后无法经视图菜单恢复（逻辑非 QSS，但样式勿隐藏菜单项）。
- 禁止 float 窗口使用浅色 OS 标题栏不处理（float 时仍应用 QSS）。

## 相关文档

- `08_Dock_System.md`
- `10_Form_System.md`
- `dark_theme_tokens.qss.md`
