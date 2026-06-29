# Navigation QSS — 左侧导航

## 设计目标

56↔180 导航轨，checked 左蓝条。

## objectName

`leftNavigationBar`、`navScanButton`、`navDeviceButton`、`navAnalysisButton`、`navReportButton`。

## QSS 片段

```css
QWidget#leftNavigationBar {
    background-color: #0B1724;
    border-right: 1px solid #1E2D3D;
    min-width: 56px;
    max-width: 180px;
}

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

## 禁止事项

- 禁止 QListWidget 默认选中样式未覆盖

## 相关

- [../02_Components/NavigationBar.md](../02_Components/NavigationBar.md)
- 历史：`../qss/button_qss_guide.md` 导航段
