# Toolbar QSS — 工具栏

## 设计目标

56px 固定高，flat icon 按钮。

## objectName

`mainToolBar`、`toolbarStartScanButton`、`toolbarStopScanButton` 等。

## QSS 片段

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

QToolButton#toolbarStopScanButton {
    color: #EF4444;
}

QToolButton#toolbarStopScanButton:disabled {
    color: #6B7280;
}
```

## 禁止事项

- 禁止 toolBar 换行增高

## 历史

吸收自 `../qss/main_window_qss_guide.md`、`../qss/button_qss_guide.md`。
