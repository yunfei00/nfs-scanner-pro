# Table — 数据表格组件

## 设计目标

明细数据按需查看，默认在 dataTableDock 隐藏。

## 使用场景

扫描点列表、频谱抽样、报告预览。

## 尺寸/颜色/状态规则

行高 32；表头 36；斑马纹 `color.bg.table.stripe`；选中 `color.table.selected`；数值列右对齐 mono。

## Qt/PySide6 推荐组件

`QTableView` + `QAbstractTableModel`；`SelectRows`。

## objectName 命名建议

```text
dataTableView
dataTableDock
scanPointTableModel
```

## 禁止事项

- 禁止 dataTableDock 默认显示
- 禁止扫描中高频 resetModel
- 禁止表格替代热力图主界面

## 相关文档

- 历史：`../11_Table_System.md`
- [../06_QSS/table_qss.md](../06_QSS/table_qss.md)
