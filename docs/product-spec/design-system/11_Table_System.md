# 11 表格系统规范

> **历史兼容**：该文档已迁移到 `02_Components/Table.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Table System

## 设计目标

数据表格用于**按需查看**扫描点、频谱读数等明细，默认隐藏在 `dataTableDock`，风格紧凑如仪器软件数据表，非 ERP 宽表。

## 使用场景

- 扫描点坐标与测量值列表
- 频谱迹线数据抽样表
- 报告字段预览（报告页可选）

## 尺寸与样式

| 属性 | 值 |
|---|---|
| 行高 | 32 px |
| 表头高 | 36 px |
| 字号 | 13 px |
| 表头字重 | 600 |
| 背景 | `--color-bg-panel` |
| 斑马纹 | `--color-table-stripe` |
| 选中行 | `--color-table-selected` |
| 网格线 | 1px `--color-divider` 水平为主 |
| 表头背景 | `--color-bg-deep` |

## 列规则

- 数值列右对齐，等宽字体。
- 文本列左对齐。
- 状态列居中，可用颜色点。
- 列宽可调，`QHeaderView.Interactive`。
- 默认显示列：序号、X、Y、Z、值(dBµV/m)、通道、时间戳。

## 状态规则

| 状态 | 表现 |
|---|---|
| 空数据 | 中央「暂无数据，请先完成扫描」 |
| 扫描中 | 尾部追加行或节流刷新（≤5Hz） |
| 只读 | 不可编辑单元格 |
| 导出 | 工具菜单或右键，非表格内置大按钮 |

## Qt/PySide6 推荐组件

- `QTableView` + `QAbstractTableModel`（大数据量）
- 小数据：`QTableWidget` 仅 Mock 阶段可用
- 表头：`QHeaderView`，禁止拖拽排序除非明确需求
- 选择：`SelectRows`，单选为主
- 滚动：`ScrollPerPixel`
- 嵌入：`dataTableDock` 内 `QWidget` 全填充

## objectName 命名建议

```text
dataTableDock
dataTableView
dataTableHeader
scanPointTableModel
```

## 禁止事项

- 禁止 dataTableDock 默认显示。
- 禁止在表格内嵌复杂 widget（进度条、图表）占满行高。
- 禁止扫描过程中全表 `resetModel` 每秒多次（性能）。
- 禁止用表格作为主扫描界面替代画布热力图。
- 禁止纯白表格背景。

## 相关文档

- Dock：`08_Dock_System.md`
- 排版：`02_Typography.md`
