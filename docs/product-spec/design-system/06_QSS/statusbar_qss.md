# StatusBar QSS — 状态栏与设备状态栏

## 设计目标

底部 32px + 设备 40px 双栏样式。

## objectName

`statusBar`、`deviceStatusBar`。

## QSS 片段

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

QWidget#deviceStatusBar {
    background-color: #0B1724;
    border-bottom: 1px solid #1E2D3D;
    min-height: 40px;
    max-height: 40px;
}

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

## 禁止事项

- 禁止 statusBar 多行

## 历史

吸收自 `../qss/main_window_qss_guide.md` StatusBar 段。
