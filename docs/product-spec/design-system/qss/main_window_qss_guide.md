# 主窗口 QSS 编写指南

> **历史兼容**：已迁移到 `06_QSS/main_window_qss.md`、`06_QSS/toolbar_qss.md`、`06_QSS/statusbar_qss.md`。

> 菜单栏、工具栏、状态栏、中央区背景

## 设计目标

主窗口 chrome 区域视觉统一、高度固定，不抢画布注意力。

## 适用 objectName

```text
mainWindow
menuBar
mainToolBar
statusBar
centralWidget
deviceStatusBar
leftNavigationBar
```

## QSS 结构建议

### QMainWindow

```css
QMainWindow#mainWindow {
    background-color: #07111D;
}
```

### QMenuBar

```css
QMenuBar {
    background-color: #07111D;
    color: #EAF2FF;
    spacing: 8px;
    min-height: 32px;
    max-height: 32px;
    border-bottom: 1px solid #1E2D3D;
}

QMenuBar::item {
    padding: 6px 12px;
    background: transparent;
}

QMenuBar::item:selected {
    background-color: #1E2D3D80;
}

QMenu {
    background-color: #0B1724;
    color: #EAF2FF;
    border: 1px solid #1E2D3D;
    padding: 4px 0;
}

QMenu::item {
    padding: 8px 32px 8px 16px;
}

QMenu::item:selected {
    background-color: #0D6EFD26;
}

QMenu::item:disabled {
    color: #6B7280;
}

QMenu::separator {
    height: 1px;
    background: #1E2D3D;
    margin: 4px 8px;
}
```

### QToolBar

```css
QToolBar#mainToolBar {
    background-color: #0A1520;
    border: none;
    border-bottom: 1px solid #1E2D3D;
    spacing: 8px;
    padding: 0 8px;
    min-height: 56px;
    max-height: 56px;
}

QToolBar QToolButton {
    background: transparent;
    border: none;
    border-radius: 4px;
    padding: 6px;
    color: #A8B3C2;
}

QToolBar QToolButton:hover {
    background-color: #1E2D3D80;
    color: #EAF2FF;
}

QToolBar QToolButton:pressed,
QToolBar QToolButton:checked {
    background-color: #0D6EFD26;
    color: #0D6EFD;
}
```

### QStatusBar

```css
QStatusBar {
    background-color: #07111D;
    color: #A8B3C2;
    border-top: 1px solid #1E2D3D;
    min-height: 32px;
    max-height: 32px;
}

QStatusBar::item {
    border: none;
}
```

### 设备状态栏（自定义 QWidget）

对 `#deviceStatusBar` 设置 panel 背景；内部 QLabel 指示点用 `setStyleSheet` 或 property class：

```css
QWidget#deviceStatusBar {
    background-color: #0B1724;
    border-bottom: 1px solid #1E2D3D;
    min-height: 40px;
    max-height: 40px;
}
```

### 左侧导航

见 `07_Navigation_System.md`，选择器 `#leftNavigationBar QToolButton`。

## 禁止事项

- 禁止 menuBar / toolBar 高度随内容增长。
- 禁止 statusBar 显示可点击链接样式（非浏览器）。
- 禁止 centralWidget 白色背景。
- 禁止在 QSS 中写 `height: 100%` 破坏固定高度布局。

## 相关文档

- `05_Menu_System.md`
- `06_Toolbar_System.md`
- `09_Status_System.md`
- `dark_theme_tokens.qss.md`
