# Table QSS — 数据表格

## 设计目标

紧凑 32px 行高，深色斑马纹。

## objectName

`dataTableView`。

## QSS 片段

```css
QTableView {
    background-color: #0B1724;
    color: #EAF2FF;
    gridline-color: #1E2D3D;
    border: 1px solid #1E2D3D;
    selection-background-color: #0D6EFD33;
    selection-color: #EAF2FF;
    alternate-background-color: #0F1A28;
}

QHeaderView::section {
    background-color: #07111D;
    color: #EAF2FF;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #1E2D3D;
    font-weight: 600;
}
```

## 禁止事项

- 禁止白底表格
- 禁止行高 < 28px

## 相关

- [../02_Components/Table.md](../02_Components/Table.md)
