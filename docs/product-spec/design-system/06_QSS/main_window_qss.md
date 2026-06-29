# Main Window QSS — 主窗口与菜单

> Token：`color.bg.app`、`size.menubar.height`。完整映射见 [token_mapping_qss.md](token_mapping_qss.md)。

## 设计目标

MenuBar 32px + Central 深色底，不抢画布。

## objectName

`mainWindow`、`menuBar`、`centralWidget`。

## QSS 片段

```css
QMainWindow#mainWindow {
    background-color: #07111D; /* color.bg.app */
}

QWidget#centralWidget {
    background-color: #050A12; /* color.bg.canvas */
}

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

## 禁止事项

- 禁止 menuBar 高度 ≠ 32px
- 禁止 centralWidget 白底

## 历史

吸收自 `../qss/main_window_qss_guide.md`（Menu 部分）。
